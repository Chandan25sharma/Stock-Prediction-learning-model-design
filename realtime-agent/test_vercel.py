#!/usr/bin/env python3
"""
Vercel Deployment Test Script
This script tests if the application is ready for Vercel deployment.
"""

import sys
import os
import importlib.util

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    required_modules = [
        'flask',
        'numpy',
        'pandas',
        'sklearn',
        'json',
        'time',
        'datetime'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_api_structure():
    """Test if the API structure is correct for Vercel."""
    print("\nTesting API structure...")
    
    # Check if api/index.py exists
    api_file = os.path.join('api', 'index.py')
    if not os.path.exists(api_file):
        print(f"✗ {api_file} not found")
        return False
    
    print(f"✓ {api_file} exists")
    
    # Check if vercel.json exists
    vercel_config = 'vercel.json'
    if not os.path.exists(vercel_config):
        print(f"✗ {vercel_config} not found")
        return False
    
    print(f"✓ {vercel_config} exists")
    
    # Check if requirements.txt exists
    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        print(f"✗ {requirements_file} not found")
        return False
    
    print(f"✓ {requirements_file} exists")
    
    return True

def test_api_loading():
    """Test if the API can be loaded successfully."""
    print("\nTesting API loading...")
    
    try:
        # Add the api directory to Python path
        api_dir = os.path.join(os.getcwd(), 'api')
        if api_dir not in sys.path:
            sys.path.insert(0, api_dir)
        
        # Import the API module
        spec = importlib.util.spec_from_file_location("api", os.path.join('api', 'index.py'))
        if spec is None or spec.loader is None:
            print("✗ Could not load API module spec")
            return False
        
        api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_module)
        
        print("✓ API module loaded successfully")
        
        # Check if Flask app exists
        if hasattr(api_module, 'app'):
            print("✓ Flask app found")
        else:
            print("✗ Flask app not found")
            return False
        
        # Check if required routes exist
        routes = [
            '/',
            '/api/status',
            '/balance',
            '/inventory',
            '/queue',
            '/trade',
            '/reset'
        ]
        
        app = api_module.app
        existing_routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        missing_routes = []
        for route in routes:
            if route not in existing_routes:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"✗ Missing routes: {missing_routes}")
            return False
        
        print("✓ All required routes found")
        return True
        
    except Exception as e:
        print(f"✗ Error loading API: {e}")
        return False

def test_file_sizes():
    """Test if file sizes are reasonable for Vercel."""
    print("\nTesting file sizes...")
    
    # Check API file size (should be < 50MB for Vercel)
    api_file = os.path.join('api', 'index.py')
    if os.path.exists(api_file):
        size = os.path.getsize(api_file)
        size_mb = size / (1024 * 1024)
        
        if size_mb > 50:
            print(f"✗ API file too large: {size_mb:.2f}MB (limit: 50MB)")
            return False
        else:
            print(f"✓ API file size: {size_mb:.2f}MB")
    
    # Check if model file exists and its size
    model_file = 'model.pkl'
    if os.path.exists(model_file):
        size = os.path.getsize(model_file)
        size_mb = size / (1024 * 1024)
        
        if size_mb > 50:
            print(f"⚠ Model file large: {size_mb:.2f}MB (may cause issues)")
        else:
            print(f"✓ Model file size: {size_mb:.2f}MB")
    
    return True

def main():
    """Main test function."""
    print("=" * 60)
    print("Vercel Deployment Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("API Structure Test", test_api_structure),
        ("API Loading Test", test_api_loading),
        ("File Size Test", test_file_sizes)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Your application is ready for Vercel deployment.")
        print("\nNext steps:")
        print("1. Run: vercel login")
        print("2. Run: vercel --prod")
        print("3. Follow the prompts to deploy")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
