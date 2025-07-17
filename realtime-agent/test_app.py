#!/usr/bin/env python3
"""
Test script for Stock Trading Agent Web Application
This script tests the main functionality of the trading agent.
"""

import requests
import json
import time
import sys

def test_api_endpoint(url, expected_status=200, description=""):
    """Test an API endpoint."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✓ {description}: {response.status_code}")
            return True, response.json() if response.headers.get('content-type') == 'application/json' else response.text
        else:
            print(f"✗ {description}: Expected {expected_status}, got {response.status_code}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"✗ {description}: Connection error - {e}")
        return False, None

def main():
    """Main test function."""
    print("=" * 60)
    print("Stock Trading Agent - Test Script")
    print("=" * 60)
    
    base_url = "http://localhost:8005"
    
    # Test if server is running
    print("Testing server availability...")
    success, _ = test_api_endpoint(f"{base_url}/api/status", description="API Status")
    if not success:
        print("Server is not running. Please start the application first.")
        sys.exit(1)
    
    # Test balance endpoint
    print("\nTesting balance endpoint...")
    success, balance = test_api_endpoint(f"{base_url}/balance", description="Balance")
    if success:
        print(f"  Current balance: ${balance}")
    
    # Test inventory endpoint
    print("\nTesting inventory endpoint...")
    success, inventory = test_api_endpoint(f"{base_url}/inventory", description="Inventory")
    if success and inventory is not None:
        print(f"  Current inventory: {len(inventory)} items")
    
    # Test queue endpoint
    print("\nTesting queue endpoint...")
    success, queue = test_api_endpoint(f"{base_url}/queue", description="Queue")
    if success and queue is not None:
        print(f"  Queue size: {len(queue)} items")
    
    # Test trade endpoint
    print("\nTesting trade endpoint...")
    trade_data = [150.25, 1000000]  # [close_price, volume]
    trade_url = f"{base_url}/trade?data={json.dumps(trade_data)}"
    success, trade_result = test_api_endpoint(trade_url, description="Trade execution")
    if success:
        print(f"  Trade result: {trade_result}")
    
    # Test reset endpoint
    print("\nTesting reset endpoint...")
    reset_url = f"{base_url}/reset?money=10000"
    success, reset_result = test_api_endpoint(reset_url, description="Reset agent")
    if success:
        print(f"  Reset result: {reset_result}")
    
    # Test web interface
    print("\nTesting web interface...")
    success, _ = test_api_endpoint(base_url, description="Web interface")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    print(f"\nWeb interface available at: {base_url}")
    print("You can now use the web interface to interact with the trading agent.")

if __name__ == "__main__":
    main()
