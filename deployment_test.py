#!/usr/bin/env python3
"""
Deployment Test Script for Django Fitness Tracker
Tests all critical functionality after deployment
"""

import requests
import json
import sys
from urllib.parse import urljoin

class DeploymentTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        
    def test_homepage(self):
        """Test if homepage loads correctly"""
        print("🏠 Testing homepage...")
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("✅ Homepage loads successfully")
                return True
            else:
                print(f"❌ Homepage failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Homepage error: {e}")
            return False
    
    def test_api_root(self):
        """Test if API root is accessible"""
        print("🔌 Testing API root...")
        try:
            url = urljoin(self.base_url, '/api/')
            response = self.session.get(url)
            if response.status_code == 200:
                print("✅ API root accessible")
                return True
            else:
                print(f"❌ API root failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API root error: {e}")
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        print("👤 Testing user registration...")
        try:
            url = urljoin(self.base_url, '/api/register/')
            data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            }
            response = self.session.post(url, json=data)
            if response.status_code in [200, 201]:
                print("✅ User registration works")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def test_user_login(self):
        """Test user login and get auth token"""
        print("🔐 Testing user login...")
        try:
            url = urljoin(self.base_url, '/api/login/')
            data = {
                'username': 'testuser',
                'password': 'testpass123'
            }
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    self.session.headers.update({
                        'Authorization': f'Token {self.auth_token}'
                    })
                    print("✅ User login successful")
                    return True
                else:
                    print("❌ Login response missing token")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_workout_creation(self):
        """Test workout session creation"""
        print("💪 Testing workout creation...")
        if not self.auth_token:
            print("❌ No auth token, skipping workout test")
            return False
            
        try:
            url = urljoin(self.base_url, '/api/workouts/')
            data = {
                'workout_type': 'cardio',
                'duration': 30,
                'intensity': 7,
                'calories_burned': 250,
                'notes': 'Test workout from deployment script'
            }
            response = self.session.post(url, json=data)
            if response.status_code in [200, 201]:
                print("✅ Workout creation works")
                return True
            else:
                print(f"❌ Workout creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Workout creation error: {e}")
            return False
    
    def test_admin_panel(self):
        """Test if admin panel is accessible"""
        print("🔧 Testing admin panel...")
        try:
            url = urljoin(self.base_url, '/admin/')
            response = self.session.get(url)
            if response.status_code == 200:
                print("✅ Admin panel accessible")
                return True
            else:
                print(f"❌ Admin panel failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Admin panel error: {e}")
            return False
    
    def test_static_files(self):
        """Test if static files are being served"""
        print("📁 Testing static files...")
        try:
            # Test common static file paths
            static_paths = [
                '/static/js/database.js',
                '/static/js/recommendation_engine.js',
                '/static/css/style.css'
            ]
            
            success_count = 0
            for path in static_paths:
                url = urljoin(self.base_url, path)
                response = self.session.head(url)
                if response.status_code == 200:
                    success_count += 1
            
            if success_count > 0:
                print(f"✅ Static files working ({success_count}/{len(static_paths)} found)")
                return True
            else:
                print("❌ No static files found")
                return False
        except Exception as e:
            print(f"❌ Static files error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all deployment tests"""
        print("🚀 Starting Deployment Tests")
        print("=" * 50)
        
        tests = [
            self.test_homepage,
            self.test_api_root,
            self.test_admin_panel,
            self.test_static_files,
            self.test_user_registration,
            self.test_user_login,
            self.test_workout_creation,
        ]
        
        results = []
        for test in tests:
            result = test()
            results.append(result)
            print()
        
        print("=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(results)
        total = len(results)
        
        print(f"Tests Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Deployment successful!")
            return True
        else:
            print("⚠️  Some tests failed. Check the issues above.")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python deployment_test.py <your-app-url>")
        print("Example: python deployment_test.py https://your-app.railway.app")
        sys.exit(1)
    
    app_url = sys.argv[1]
    tester = DeploymentTester(app_url)
    
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
