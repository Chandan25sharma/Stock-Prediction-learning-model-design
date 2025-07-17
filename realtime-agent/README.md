# Stock Trading Agent - Real-time Web Application

A Flask-based web application for real-time stock trading using an Evolution Strategy AI agent.

## Features

- 🤖 AI-powered trading agent using Deep Evolution Strategy
- 📊 Real-time web interface for monitoring and trading
- 📈 Live balance and inventory tracking
- 🔄 Reset functionality for testing different scenarios
- 📱 Responsive web design
- 🐳 Docker support for easy deployment

## Quick Start

### Method 1: Using Startup Scripts

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### Method 2: Manual Setup

1. **Install Python 3.7+** if not already installed

2. **Create virtual environment:**
```bash
python -m venv .venv
```

3. **Activate virtual environment:**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Install requirements:**
```bash
pip install -r requirements.txt
```

5. **Run the application:**
```bash
python app.py
```

### Method 3: Docker

```bash
docker build -t stock-trading-agent .
docker run -p 8005:8005 stock-trading-agent
```

## Usage

1. **Open your browser** and navigate to `http://localhost:8005`

2. **Monitor Agent Status:**
   - View current balance
   - Check inventory holdings
   - Monitor data queue size

3. **Execute Trades:**
   - Enter close price and volume
   - Click "Execute Trade"
   - View results in real-time

4. **Reset Agent:**
   - Set new initial capital
   - Reset to start fresh testing

## API Endpoints

- `GET /` - Web interface
- `GET /api/status` - API status
- `GET /balance` - Current balance
- `GET /inventory` - Current inventory
- `GET /queue` - Data queue
- `GET /trade?data=[close_price, volume]` - Execute trade
- `GET /reset?money=amount` - Reset agent

## Training the Model

The application uses a pre-trained model (`model.pkl`). To train your own model:

1. **Open the Jupyter notebook:**
```bash
jupyter notebook realtime-evolution-strategy.ipynb
```

2. **Follow the training process** in the notebook

3. **The trained model** will be saved as `model.pkl`

The model was trained on multiple stocks:
```python
['TWTR.csv', 'GOOG.csv', 'FB.csv', 'LB.csv', 'MTDR.csv', 
 'CPRT.csv', 'FSV.csv', 'TSLA.csv', 'SINA.csv', 'GWR.csv']
```

## Model Architecture

The agent uses Deep Evolution Strategy with:
- **Input:** Stock price and volume data
- **Window Size:** 20 time periods
- **Layer Size:** 500 neurons
- **Output:** 3 actions (hold, buy, sell)
- **Population Size:** 15 for evolution
- **Learning Rate:** 0.03

## Data Format

The agent expects stock data in CSV format with columns:
- `Close` - Closing price
- `Volume` - Trading volume

Sample data files included:
- TWTR.csv (Twitter stock data)
- TSLA.csv (Tesla stock data)
- GOOG.csv (Google stock data)
- And more...

## API Examples

### Execute a Trade
```bash
curl "http://localhost:8005/trade?data=[150.25,1000000]"
```

Response:
```json
{
  "action": "buy",
  "balance": 9849.75,
  "status": "buy 1 unit, cost 150.25",
  "timestamp": "2025-07-17 10:30:15.123456"
}
```

### Check Balance
```bash
curl "http://localhost:8005/balance"
```

### Reset Agent
```bash
curl "http://localhost:8005/reset?money=10000"
```

## Configuration

Edit the following variables in `app.py`:
- `window_size` - Historical data window (default: 20)
- `skip` - Data skip interval (default: 1)
- `layer_size` - Neural network layer size (default: 500)
- `output_size` - Number of actions (default: 3)

## Troubleshooting

### Common Issues:

1. **Model file not found:**
   - Train the model using the Jupyter notebook
   - Ensure `model.pkl` is in the same directory

2. **Data file not found:**
   - Ensure CSV files are in the same directory
   - Check file format matches expected columns

3. **Port already in use:**
   - Change port in `app.py`: `app.run(host='0.0.0.0', port=8006)`

4. **Dependencies not installed:**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## Performance Notes

- The agent works best with sufficient historical data (>20 periods)
- Performance depends on the quality of training data
- Consider retraining for different market conditions

## Integration

You can integrate this with:
- Real-time socket connections
- Stock market APIs
- Custom data feeds
- Web applications

## License

This project is licensed under the Apache License 2.0.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the Jupyter notebook for training details
3. Open an issue on GitHub
