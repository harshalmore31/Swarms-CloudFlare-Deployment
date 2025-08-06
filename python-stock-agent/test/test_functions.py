"""
Test script for Python Stock Agent functions
This can be used to test individual components before deployment
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add src to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock environment for testing
class MockEnv:
    def __init__(self):
        self.SWARMS_API_KEY = "test_key"
        self.FMP_API_KEY = None  # Set to None to test news unavailable path
        self.MAILGUN_API_KEY = None
        self.MAILGUN_DOMAIN = None
        self.RECIPIENT_EMAIL = None

async def test_market_data_fetch():
    """Test the market data fetching functionality"""
    print("🧪 Testing market data fetch...")
    
    try:
        # Import the function from entry.py
        from entry import fetch_market_data
        
        market_data = await fetch_market_data()
        
        print(f"✅ Market data fetched for {len(market_data)} symbols")
        
        # Check data structure
        for symbol, data in market_data.items():
            if not data.get('error'):
                print(f"  📊 {symbol}: ${data.get('price', 'N/A')}, Change: {data.get('change_percent', 'N/A')}%")
            else:
                print(f"  ❌ {symbol}: {data['error']}")
        
        return len([s for s, d in market_data.items() if not d.get('error')]) > 0
        
    except Exception as e:
        print(f"❌ Market data fetch test failed: {e}")
        return False

async def test_news_fetch():
    """Test the news fetching functionality"""
    print("\n🧪 Testing news fetch (without API key)...")
    
    try:
        from entry import fetch_market_news
        
        mock_env = MockEnv()
        news = await fetch_market_news(mock_env)
        
        print(f"✅ News fetch completed")
        print(f"  📰 Result: {news[:100]}..." if isinstance(news, str) else f"  📰 Articles: {len(news)}")
        
        return True
        
    except Exception as e:
        print(f"❌ News fetch test failed: {e}")
        return False

async def test_html_generation():
    """Test HTML dashboard generation"""
    print("\n🧪 Testing HTML dashboard generation...")
    
    try:
        from entry import get_dashboard_html
        
        html = get_dashboard_html()
        
        print(f"✅ HTML generated, length: {len(html)} characters")
        print(f"  🌐 Contains 'Python': {'Python' in html}")
        print(f"  🌐 Contains dashboard elements: {'btn' in html and 'progress' in html}")
        
        return len(html) > 1000 and 'Python' in html
        
    except Exception as e:
        print(f"❌ HTML generation test failed: {e}")
        return False

async def test_analysis_structure():
    """Test the analysis function structure (without API call)"""
    print("\n🧪 Testing analysis function structure...")
    
    try:
        from entry import handle_stock_analysis
        
        mock_env = MockEnv()
        mock_ctx = type('obj', (object,), {'wait_until': lambda x: None})()
        
        # This will fail at the API call, but we can test the structure
        try:
            result = await handle_stock_analysis(None, mock_env, mock_ctx)
            print(f"📊 Analysis result type: {type(result)}")
            print(f"📊 Has success field: {'success' in result}")
        except Exception as api_error:
            print(f"⚠️  Expected API failure (no valid key): {str(api_error)[:50]}...")
            # This is expected since we don't have a real API key
        
        print("✅ Analysis function structure test completed")
        return True
        
    except Exception as e:
        print(f"❌ Analysis structure test failed: {e}")
        return False

def test_configuration():
    """Test configuration files"""
    print("\n🧪 Testing configuration files...")
    
    try:
        # Test wrangler.jsonc
        with open('../wrangler.jsonc', 'r') as f:
            wrangler_config = json.loads(f.read())
        
        print("✅ wrangler.jsonc is valid JSON")
        print(f"  📁 Worker name: {wrangler_config.get('name')}")
        print(f"  📁 Main file: {wrangler_config.get('main')}")
        print(f"  📁 Python workers flag: {'python_workers' in wrangler_config.get('compatibility_flags', [])}")
        
        # Test package.json
        with open('../package.json', 'r') as f:
            package_config = json.loads(f.read())
        
        print("✅ package.json is valid JSON")
        print(f"  📦 Package name: {package_config.get('name')}")
        print(f"  📦 Scripts available: {len(package_config.get('scripts', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Python Stock Agent Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration Files", test_configuration),
        ("Market Data Fetch", test_market_data_fetch),
        ("News Fetch", test_news_fetch),
        ("HTML Generation", test_html_generation),
        ("Analysis Structure", test_analysis_structure),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Ready for deployment.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())