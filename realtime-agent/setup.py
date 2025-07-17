#!/usr/bin/env python3
"""
Setup script for Stock Trading Agent Web Application
This script sets up the environment and dependencies for the trading agent.
"""

import os
import sys
import subprocess
import venv
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path('.venv')
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create('.venv', with_pip=True)
        print("Virtual environment created successfully!")
    else:
        print("Virtual environment already exists.")

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    # Determine the correct pip path
    if sys.platform == "win32":
        pip_path = Path('.venv/Scripts/pip.exe')
        python_path = Path('.venv/Scripts/python.exe')
    else:
        pip_path = Path('.venv/bin/pip')
        python_path = Path('.venv/bin/python')
    
    # Install dependencies
    dependencies = [
        "Flask==2.3.3",
        "numpy==1.24.3",
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "Werkzeug==2.3.7"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        result = run_command(f"{pip_path} install {dep}")
        if result is None:
            print(f"Failed to install {dep}")
            return False
    
    print("All dependencies installed successfully!")
    return True

def check_data_files():
    """Check if required data files exist."""
    print("Checking data files...")
    
    required_files = ['TWTR.csv', 'model.pkl']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"Warning: Missing files: {', '.join(missing_files)}")
        
        if 'model.pkl' in missing_files:
            print("Note: model.pkl will be created automatically when the app starts.")
        
        if 'TWTR.csv' in missing_files:
            print("Note: You may need to provide your own stock data CSV file.")
            print("The CSV should have 'Close' and 'Volume' columns.")
    else:
        print("All required files are present!")

def create_startup_scripts():
    """Create startup scripts for different platforms."""
    print("Creating startup scripts...")
    
    # Windows batch script
    bat_content = '''@echo off
echo Starting Stock Trading Agent...
echo.

REM Activate virtual environment
call .venv\\Scripts\\activate

REM Start the Flask application
echo Starting Flask application...
echo The application will be available at http://localhost:8005
echo Press Ctrl+C to stop the server
echo.
python app.py
'''
    
    with open('start.bat', 'w') as f:
        f.write(bat_content)
    
    # Unix shell script
    sh_content = '''#!/bin/bash

echo "Starting Stock Trading Agent..."
echo

# Activate virtual environment
source .venv/bin/activate

# Start the Flask application
echo "Starting Flask application..."
echo "The application will be available at http://localhost:8005"
echo "Press Ctrl+C to stop the server"
echo
python app.py
'''
    
    with open('start.sh', 'w') as f:
        f.write(sh_content)
    
    # Make shell script executable on Unix systems
    if sys.platform != "win32":
        os.chmod('start.sh', 0o755)
    
    print("Startup scripts created successfully!")

def create_requirements_file():
    """Create a requirements.txt file."""
    print("Creating requirements.txt...")
    
    requirements_content = '''Flask==2.3.3
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
Werkzeug==2.3.7
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)
    
    print("requirements.txt created successfully!")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Stock Trading Agent - Setup Script")
    print("=" * 60)
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create virtual environment
    create_virtual_environment()
    
    # Create requirements file
    create_requirements_file()
    
    # Install dependencies
    if not install_dependencies():
        print("Setup failed due to dependency installation errors.")
        return False
    
    # Check data files
    check_data_files()
    
    # Create startup scripts
    create_startup_scripts()
    
    print("\n" + "=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    
    print("\nTo start the application:")
    print("  Windows: start.bat")
    print("  Linux/Mac: ./start.sh")
    print("\nOr manually:")
    
    if sys.platform == "win32":
        print("  .venv\\Scripts\\activate")
    else:
        print("  source .venv/bin/activate")
    
    print("  python app.py")
    print("\nThe application will be available at http://localhost:8005")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
