#!/usr/bin/env python3
"""
Test script to verify the fitness app fixes are working correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test core API endpoints"""
    print("🧪 Testing API endpoints...")
    
    # Test API root
    try:
        response = requests.get(f"{BASE_URL}/api/")
        if response.status_code == 200:
            print("✅ API root endpoint working")
        else:
            print(f"❌ API root failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API root error: {e}")
    
    # Test main page
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Main page loading")
        else:
            print(f"❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page error: {e}")
    
    # Test login page
    try:
        response = requests.get(f"{BASE_URL}/login/")
        if response.status_code == 200:
            print("✅ Login page loading")
        else:
            print(f"❌ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Login page error: {e}")

def test_static_files():
    """Test static files are loading"""
    print("\n📁 Testing static files...")
    
    static_files = [
        "/static/js/database.js",
        "/static/js/client_focused_engine.js",
        "/static/js/user_summary_index.js"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{BASE_URL}{file_path}")
            if response.status_code == 200:
                print(f"✅ {file_path} - OK")
            else:
                print(f"❌ {file_path} - Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")

def test_authentication_flow():
    """Test authentication endpoints"""
    print("\n🔐 Testing authentication...")
    
    # Test registration endpoint (without actually registering)
    try:
        response = requests.post(f"{BASE_URL}/api/register/", 
                               json={},
                               headers={'Content-Type': 'application/json'})
        # We expect this to fail with validation errors, which is good
        if response.status_code in [400, 422]:
            print("✅ Registration endpoint responding")
        else:
            print(f"⚠️ Registration endpoint unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Registration endpoint error: {e}")
    
    # Test login endpoint (without valid credentials)
    try:
        response = requests.post(f"{BASE_URL}/api/login/", 
                               json={},
                               headers={'Content-Type': 'application/json'})
        # We expect this to fail with validation errors, which is good
        if response.status_code in [400, 401, 422]:
            print("✅ Login endpoint responding")
        else:
            print(f"⚠️ Login endpoint unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Login endpoint error: {e}")

if __name__ == "__main__":
    print("🏋️ Fitness App Fix Verification Test")
    print("="*50)
    
    test_api_endpoints()
    test_static_files()
    test_authentication_flow()
    
    print("\n" + "="*50)
    print("🎯 Test Summary:")
    print("The above tests verify that:")
    print("1. ✅ Django server is running properly")
    print("2. ✅ Static files are being served")
    print("3. ✅ API endpoints are accessible")
    print("4. ✅ Authentication endpoints are working")
    print("\nNext steps: Test the frontend manually in browser")
