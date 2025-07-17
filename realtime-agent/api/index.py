from flask import Flask, request, jsonify, render_template_string
import numpy as np
import pickle
import json
import time
import os
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from datetime import datetime

app = Flask(__name__)

window_size = 20
skip = 1
layer_size = 500
output_size = 3

def softmax(z):
    assert len(z.shape) == 2
    s = np.max(z, axis=1)
    s = s[:, np.newaxis]
    e_x = np.exp(z - s)
    div = np.sum(e_x, axis=1)
    div = div[:, np.newaxis]
    return e_x / div

def get_state(parameters, t, window_size = 20):
    outside = []
    d = t - window_size + 1
    for parameter in parameters:
        block = (
            parameter[d : t + 1]
            if d >= 0
            else -d * [parameter[0]] + parameter[0 : t + 1]
        )
        res = []
        for i in range(window_size - 1):
            res.append(block[i + 1] - block[i])
        for i in range(1, window_size, 1):
            res.append(block[i] - block[0])
        outside.append(res)
    return np.array(outside).reshape((1, -1))


class Deep_Evolution_Strategy:

    inputs = None

    def __init__(
        self, weights, reward_function, population_size, sigma, learning_rate
    ):
        self.weights = weights
        self.reward_function = reward_function
        self.population_size = population_size
        self.sigma = sigma
        self.learning_rate = learning_rate

    def _get_weight_from_population(self, weights, population):
        weights_population = []
        for index, i in enumerate(population):
            jittered = self.sigma * i
            weights_population.append(weights[index] + jittered)
        return weights_population

    def get_weights(self):
        return self.weights
    
    def train(self, epoch = 100, print_every = 1):
        lasttime = time.time()
        for i in range(epoch):
            population = []
            rewards = np.zeros(self.population_size)
            for k in range(self.population_size):
                x = []
                for w in self.weights:
                    x.append(np.random.randn(*w.shape))
                population.append(x)
            for k in range(self.population_size):
                weights_population = self._get_weight_from_population(
                    self.weights, population[k]
                )
                rewards[k] = self.reward_function(weights_population)
            rewards = (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-7)
            for index, w in enumerate(self.weights):
                A = np.array([p[index] for p in population])
                self.weights[index] = (
                    w
                    + self.learning_rate
                    / (self.population_size * self.sigma)
                    * np.dot(A.T, rewards).T
                )
            if (i + 1) % print_every == 0:
                print(
                    'iter %d. reward: %f'
                    % (i + 1, self.reward_function(self.weights))
                )
        print('time taken to train:', time.time() - lasttime, 'seconds')
        
class Model:
    def __init__(self, input_size, layer_size, output_size):
        self.weights = [
            np.random.rand(input_size, layer_size)
            * np.sqrt(1 / (input_size + layer_size)),
            np.random.rand(layer_size, output_size)
            * np.sqrt(1 / (layer_size + output_size)),
            np.zeros((1, layer_size)),
            np.zeros((1, output_size)),
        ]

    def predict(self, inputs):
        feed = np.dot(inputs, self.weights[0]) + self.weights[-2]
        decision = np.dot(feed, self.weights[1]) + self.weights[-1]
        return decision

    def get_weights(self):
        return self.weights

    def set_weights(self, weights):
        self.weights = weights


class Agent:

    POPULATION_SIZE = 15
    SIGMA = 0.1
    LEARNING_RATE = 0.03

    def __init__(self, model, timeseries, skip, initial_money, real_trend, minmax):
        self.model = model
        self.timeseries = timeseries
        self.skip = skip
        self.real_trend = real_trend
        self.initial_money = initial_money
        self.es = Deep_Evolution_Strategy(
            self.model.get_weights(),
            self.get_reward,
            self.POPULATION_SIZE,
            self.SIGMA,
            self.LEARNING_RATE,
        )
        self.minmax = minmax
        self._initiate()

    def _initiate(self):
        # i assume first index is the close value
        self.trend = self.timeseries[0]
        self._mean = np.mean(self.trend)
        self._std = np.std(self.trend)
        self._inventory = []
        self._capital = self.initial_money
        self._queue = []
        self._scaled_capital = self.minmax.transform([[self._capital, 2]])[0, 0]

    def reset_capital(self, capital):
        if capital:
            self._capital = capital
        self._scaled_capital = self.minmax.transform([[self._capital, 2]])[0, 0]
        self._queue = []
        self._inventory = []

    def trade(self, data):
        """
        you need to make sure the data is [close, volume]
        """
        scaled_data = self.minmax.transform([data])[0]
        real_close = data[0]
        close = scaled_data[0]
        if len(self._queue) >= window_size:
            self._queue.pop(0)
        self._queue.append(scaled_data)
        if len(self._queue) < window_size:
            return {
                'status': 'data not enough to trade',
                'action': 'fail',
                'balance': self._capital,
                'timestamp': str(datetime.now()),
            }
        state = self.get_state(
            window_size - 1,
            self._inventory,
            self._scaled_capital,
            timeseries = np.array(self._queue).T.tolist(),
        )
        action, prob = self.act_softmax(state)
        print(prob)
        if action == 1 and self._scaled_capital >= close:
            self._inventory.append(close)
            self._scaled_capital -= close
            self._capital -= real_close
            return {
                'status': 'buy 1 unit, cost %f' % (real_close),
                'action': 'buy',
                'balance': self._capital,
                'timestamp': str(datetime.now()),
            }
        elif action == 2 and len(self._inventory):
            bought_price = self._inventory.pop(0)
            self._scaled_capital += close
            self._capital += real_close
            scaled_bought_price = self.minmax.inverse_transform(
                [[bought_price, 2]]
            )[0, 0]
            try:
                invest = (
                    (real_close - scaled_bought_price) / scaled_bought_price
                ) * 100
            except:
                invest = 0
            return {
                'status': 'sell 1 unit, price %f' % (real_close),
                'investment': invest,
                'gain': real_close - scaled_bought_price,
                'balance': self._capital,
                'action': 'sell',
                'timestamp': str(datetime.now()),
            }
        else:
            return {
                'status': 'do nothing',
                'action': 'nothing',
                'balance': self._capital,
                'timestamp': str(datetime.now()),
            }

    def change_data(self, timeseries, skip, initial_money, real_trend, minmax):
        self.timeseries = timeseries
        self.skip = skip
        self.initial_money = initial_money
        self.real_trend = real_trend
        self.minmax = minmax
        self._initiate()

    def act(self, sequence):
        decision = self.model.predict(np.array(sequence))

        return np.argmax(decision[0])

    def act_softmax(self, sequence):
        decision = self.model.predict(np.array(sequence))

        return np.argmax(decision[0]), softmax(decision)[0]

    def get_state(self, t, inventory, capital, timeseries):
        state = get_state(timeseries, t)
        len_inventory = len(inventory)
        if len_inventory:
            mean_inventory = np.mean(inventory)
        else:
            mean_inventory = 0
        z_inventory = (mean_inventory - self._mean) / self._std
        z_capital = (capital - self._mean) / self._std
        concat_parameters = np.concatenate(
            [state, [[len_inventory, z_inventory, z_capital]]], axis = 1
        )
        return concat_parameters

    def get_reward(self, weights):
        initial_money = self._scaled_capital
        starting_money = initial_money
        invests = []
        self.model.weights = weights
        inventory = []
        state = self.get_state(0, inventory, starting_money, self.timeseries)

        for t in range(0, len(self.trend) - 1, self.skip):
            action = self.act(state)
            if action == 1 and starting_money >= self.trend[t]:
                inventory.append(self.trend[t])
                starting_money -= self.trend[t]

            elif action == 2 and len(inventory):
                bought_price = inventory.pop(0)
                starting_money += self.trend[t]
                invest = ((self.trend[t] - bought_price) / bought_price) * 100
                invests.append(invest)

            state = self.get_state(
                t + 1, inventory, starting_money, self.timeseries
            )
        invests = np.mean(invests)
        if np.isnan(invests):
            invests = 0
        score = (starting_money - initial_money) / initial_money * 100
        return invests * 0.7 + score * 0.3

    def fit(self, iterations, checkpoint):
        self.es.train(iterations, print_every = checkpoint)

    def buy(self):
        initial_money = self._scaled_capital
        starting_money = initial_money

        real_initial_money = self.initial_money
        real_starting_money = self.initial_money
        inventory = []
        real_inventory = []
        state = self.get_state(0, inventory, starting_money, self.timeseries)
        states_sell = []
        states_buy = []

        for t in range(0, len(self.trend) - 1, self.skip):
            action, prob = self.act_softmax(state)
            print(t, prob)

            if action == 1 and starting_money >= self.trend[t] and t < (len(self.trend) - 1 - window_size):
                inventory.append(self.trend[t])
                real_inventory.append(self.real_trend[t])
                real_starting_money -= self.real_trend[t]
                starting_money -= self.trend[t]
                states_buy.append(t)
                print(
                    'day %d: buy 1 unit at price %f, total balance %f'
                    % (t, self.real_trend[t], real_starting_money)
                )

            elif action == 2 and len(inventory):
                bought_price = inventory.pop(0)
                real_bought_price = real_inventory.pop(0)
                starting_money += self.trend[t]
                real_starting_money += self.real_trend[t]
                states_sell.append(t)
                try:
                    invest = (
                        (self.real_trend[t] - real_bought_price)
                        / real_bought_price
                    ) * 100
                except:
                    invest = 0
                print(
                    'day %d, sell 1 unit at price %f, investment %f %%, total balance %f,'
                    % (t, self.real_trend[t], invest, real_starting_money)
                )
            state = self.get_state(
                t + 1, inventory, starting_money, self.timeseries
            )

        invest = (
            (real_starting_money - real_initial_money) / real_initial_money
        ) * 100
        total_gains = real_starting_money - real_initial_money
        return states_buy, states_sell, total_gains, invest

# Global variables for the agent
model = None
agent = None

def initialize_agent():
    global model, agent
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to load the model from parent directory
    model_path = os.path.join(script_dir, '..', 'model.pkl')
    try:
        with open(model_path, 'rb') as fopen:
            model = pickle.load(fopen)
            print("Model loaded successfully from:", model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        # Create a new model if loading fails
        print("Creating new model...")
        model = Model(input_size=window_size * 2 * 2 + 3, 
                     layer_size=layer_size, 
                     output_size=output_size)

    # Try to load data from parent directory
    data_path = os.path.join(script_dir, '..', 'TWTR.csv')
    try:
        df = pd.read_csv(data_path)
        print("Data loaded successfully from:", data_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        # Create sample data
        print("Creating sample data...")
        dates = pd.date_range('2020-01-01', periods=100)
        df = pd.DataFrame({
            'Close': np.random.uniform(100, 200, 100),
            'Volume': np.random.uniform(1000000, 5000000, 100)
        })
    
    real_trend = df['Close'].tolist()
    parameters = [df['Close'].tolist(), df['Volume'].tolist()]
    minmax = MinMaxScaler(feature_range = (100, 200)).fit(np.array(parameters).T)
    scaled_parameters = minmax.transform(np.array(parameters).T).T.tolist()
    initial_money = np.max(parameters[0]) * 2

    agent = Agent(model = model,
                  timeseries = scaled_parameters,
                  skip = skip,
                  initial_money = initial_money,
                  real_trend = real_trend,
                  minmax = minmax)

# Initialize the agent
initialize_agent()

# HTML template embedded in the code
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Trading Agent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .section h2 {
            color: #555;
            margin-top: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="number"], input[type="text"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        .button-danger {
            background-color: #f44336;
        }
        .button-danger:hover {
            background-color: #da190b;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            font-weight: bold;
        }
        .status.success {
            background-color: #dff0d8;
            color: #3c763d;
            border: 1px solid #d6e9c6;
        }
        .status.error {
            background-color: #f2dede;
            color: #a94442;
            border: 1px solid #ebccd1;
        }
        .status.info {
            background-color: #d9edf7;
            color: #31708f;
            border: 1px solid #bce8f1;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }
        .stat-item {
            text-align: center;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            min-width: 120px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .trade-history {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background-color: #f9f9f9;
        }
        .trade-entry {
            margin-bottom: 10px;
            padding: 8px;
            border-left: 4px solid #4CAF50;
            background-color: white;
        }
        .trade-entry.sell {
            border-left-color: #f44336;
        }
        .trade-entry.nothing {
            border-left-color: #ff9800;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Stock Trading Agent</h1>
        <p style="text-align: center; color: #666;">Deployed on Vercel</p>
        
        <div class="section">
            <h2>Agent Status</h2>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value" id="balance">$0.00</div>
                    <div class="stat-label">Balance</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="inventory">0</div>
                    <div class="stat-label">Inventory</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="queue">0</div>
                    <div class="stat-label">Queue Size</div>
                </div>
            </div>
            <button onclick="refreshStatus()">🔄 Refresh Status</button>
        </div>

        <div class="section">
            <h2>Trade Stock</h2>
            <div class="form-group">
                <label for="closePrice">Close Price:</label>
                <input type="number" id="closePrice" step="0.01" placeholder="e.g., 150.25">
            </div>
            <div class="form-group">
                <label for="volume">Volume:</label>
                <input type="number" id="volume" placeholder="e.g., 1000000">
            </div>
            <button onclick="executeTrade()">📈 Execute Trade</button>
        </div>

        <div class="section">
            <h2>Reset Agent</h2>
            <div class="form-group">
                <label for="resetMoney">Initial Money:</label>
                <input type="number" id="resetMoney" step="0.01" placeholder="e.g., 10000">
            </div>
            <button onclick="resetAgent()" class="button-danger">🔄 Reset Agent</button>
        </div>

        <div class="section">
            <h2>Trade History</h2>
            <div id="tradeHistory" class="trade-history">
                <p>No trades executed yet.</p>
            </div>
            <button onclick="clearHistory()">🗑️ Clear History</button>
        </div>

        <div id="statusMessage" class="status" style="display: none;"></div>
    </div>

    <script>
        let tradeHistory = [];
        const baseUrl = window.location.origin;

        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('statusMessage');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }

        function formatCurrency(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(amount);
        }

        function formatNumber(num) {
            return new Intl.NumberFormat('en-US').format(num);
        }

        async function refreshStatus() {
            try {
                const [balanceResp, inventoryResp, queueResp] = await Promise.all([
                    fetch('/balance'),
                    fetch('/inventory'),
                    fetch('/queue')
                ]);

                const balance = await balanceResp.json();
                const inventory = await inventoryResp.json();
                const queue = await queueResp.json();

                document.getElementById('balance').textContent = formatCurrency(balance);
                document.getElementById('inventory').textContent = inventory.length;
                document.getElementById('queue').textContent = queue.length;

                showStatus('Status refreshed successfully', 'success');
            } catch (error) {
                showStatus('Error refreshing status: ' + error.message, 'error');
            }
        }

        async function executeTrade() {
            const closePrice = document.getElementById('closePrice').value;
            const volume = document.getElementById('volume').value;

            if (!closePrice || !volume) {
                showStatus('Please enter both close price and volume', 'error');
                return;
            }

            try {
                const data = [parseFloat(closePrice), parseInt(volume)];
                const response = await fetch(`/trade?data=${JSON.stringify(data)}`);
                const result = await response.json();

                if (response.ok) {
                    addTradeToHistory(result);
                    showStatus(`Trade executed: ${result.status}`, 'success');
                    refreshStatus();
                } else {
                    showStatus(`Trade failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus('Error executing trade: ' + error.message, 'error');
            }
        }

        async function resetAgent() {
            const money = document.getElementById('resetMoney').value;

            if (!money) {
                showStatus('Please enter initial money amount', 'error');
                return;
            }

            try {
                const response = await fetch(`/reset?money=${money}`);
                const result = await response.json();

                if (response.ok) {
                    showStatus('Agent reset successfully', 'success');
                    refreshStatus();
                    clearHistory();
                } else {
                    showStatus(`Reset failed: ${result.error}`, 'error');
                }
            } catch (error) {
                showStatus('Error resetting agent: ' + error.message, 'error');
            }
        }

        function addTradeToHistory(trade) {
            tradeHistory.unshift(trade);
            if (tradeHistory.length > 50) {
                tradeHistory = tradeHistory.slice(0, 50);
            }
            updateTradeHistoryDisplay();
        }

        function updateTradeHistoryDisplay() {
            const historyDiv = document.getElementById('tradeHistory');
            
            if (tradeHistory.length === 0) {
                historyDiv.innerHTML = '<p>No trades executed yet.</p>';
                return;
            }

            historyDiv.innerHTML = tradeHistory.map(trade => `
                <div class="trade-entry ${trade.action}">
                    <strong>${trade.action.toUpperCase()}</strong>: ${trade.status}<br>
                    <small>Balance: ${formatCurrency(trade.balance)} | ${trade.timestamp}</small>
                    ${trade.investment ? `<br><small>Investment: ${trade.investment}%</small>` : ''}
                    ${trade.gain ? `<br><small>Gain: ${formatCurrency(trade.gain)}</small>` : ''}
                </div>
            `).join('');
        }

        function clearHistory() {
            tradeHistory = [];
            updateTradeHistoryDisplay();
            showStatus('Trade history cleared', 'info');
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            refreshStatus();
        });
    </script>
</body>
</html>
"""

@app.route('/', methods = ['GET'])
def hello():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status', methods = ['GET'])
def api_status():
    return jsonify({'status': 'OK', 'platform': 'Vercel'})

@app.route('/inventory', methods = ['GET'])
def inventory():
    try:
        return jsonify(agent._inventory)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/queue', methods = ['GET'])
def queue():
    try:
        return jsonify(agent._queue)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/balance', methods = ['GET'])
def balance():
    try:
        return jsonify(agent._capital)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trade', methods = ['GET'])
def trade():
    try:
        data_str = request.args.get('data')
        if not data_str:
            return jsonify({'error': 'data parameter is required'}), 400
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not isinstance(data, list) or len(data) != 2:
            return jsonify({'error': 'data must be a list with 2 elements [close_price, volume]'}), 400
        
        result = agent.trade(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods = ['GET'])
def reset():
    try:
        money_str = request.args.get('money')
        if not money_str:
            return jsonify({'error': 'money parameter is required'}), 400
        try:
            money = float(money_str)
        except ValueError:
            return jsonify({'error': 'money must be a valid number'}), 400
        
        agent.reset_capital(money)
        return jsonify({'success': True, 'message': 'Agent reset successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)
