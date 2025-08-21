#!/usr/bin/env python3
"""
Test script to verify the app can run without critical errors
Run this before deploying to catch any obvious issues
"""

import sys
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False
    
    return True

def test_app_modules():
    """Test if app-specific modules can be imported"""
    print("\n🔧 Testing app modules...")
    
    try:
        from config import INDIAN_STOCKS, DEFAULT_STOCK
        print("✅ Config imported successfully")
        print(f"   Default stock: {DEFAULT_STOCK}")
        print(f"   Available stocks: {len(INDIAN_STOCKS)}")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from advanced_indicators import AdvancedTechnicalIndicators
        print("✅ Advanced indicators imported successfully")
    except ImportError as e:
        print(f"❌ Advanced indicators import failed: {e}")
        return False
    
    try:
        from ensemble_models import EnsembleModels
        print("✅ Ensemble models imported successfully")
    except ImportError as e:
        print(f"❌ Ensemble models import failed: {e}")
        return False
    
    try:
        from realtime_data import RealTimeDataFeed
        print("✅ Real-time data imported successfully")
    except ImportError as e:
        print(f"❌ Real-time data import failed: {e}")
        return False
    
    return True

def test_web_app():
    """Test if web_app.py can be imported and basic functions exist"""
    print("\n🌐 Testing web app...")
    
    try:
        # Import the web app module
        import web_app
        print("✅ Web app imported successfully")
        
        # Check if main function exists
        if hasattr(web_app, 'main'):
            print("✅ Main function found")
        else:
            print("❌ Main function not found")
            return False
        
        # Check if EXTENDED_INDIAN_STOCKS exists
        if hasattr(web_app, 'EXTENDED_INDIAN_STOCKS'):
            print(f"✅ EXTENDED_INDIAN_STOCKS found with {len(web_app.EXTENDED_INDIAN_STOCKS)} stocks")
        else:
            print("❌ EXTENDED_INDIAN_STOCKS not found")
            return False
        
        # Check if create_custom_metric function exists
        if hasattr(web_app, 'create_custom_metric'):
            print("✅ create_custom_metric function found")
        else:
            print("❌ create_custom_metric function not found")
            return False
        
        # Check if display_stock_grid function exists
        if hasattr(web_app, 'display_stock_grid'):
            print("✅ display_stock_grid function found")
        else:
            print("❌ display_stock_grid function not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web app test failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality without running the full app"""
    print("\n⚙️ Testing basic functionality...")
    
    try:
        from config import INDIAN_STOCKS
        from advanced_indicators import AdvancedTechnicalIndicators
        
        # Test creating indicators object
        indicators = AdvancedTechnicalIndicators()
        print("✅ AdvancedTechnicalIndicators object created")
        
        # Test basic stock data
        test_stock = list(INDIAN_STOCKS.keys())[0]
        print(f"✅ Test stock selected: {test_stock}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting deployment tests...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("App Modules", test_app_modules),
        ("Web App", test_web_app),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
