#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all authentication and core endpoints
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_data = {}
        self.tokens = {}
        self.passed = 0
        self.failed = 0
        # Use timestamp to create unique test emails
        self.timestamp = int(time.time())
        
    async def close(self):
        await self.client.aclose()
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        if status == "PASS":
            self.passed += 1
            print(f"{Colors.GREEN}✓{Colors.RESET} {test_name}")
            if details:
                print(f"  {Colors.BLUE}→{Colors.RESET} {details}")
        elif status == "FAIL":
            self.failed += 1
            print(f"{Colors.RED}✗{Colors.RESET} {test_name}")
            if details:
                print(f"  {Colors.RED}Error:{Colors.RESET} {details}")
        else:
            print(f"{Colors.YELLOW}!{Colors.RESET} {test_name}: {details}")
    
    async def test_endpoint(self, method: str, endpoint: str, test_name: str, 
                           data: Optional[Dict] = None, 
                           headers: Optional[Dict] = None,
                           expected_status: int = 200) -> Optional[Dict]:
        """Test an API endpoint and return response"""
        url = f"{API_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers)
            elif method == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                try:
                    result = response.json()
                    self.log_test(test_name, "PASS", f"Status: {response.status_code}")
                    return result
                except:
                    self.log_test(test_name, "PASS", f"Status: {response.status_code} (No JSON)")
                    return {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {json.dumps(error_detail, indent=2)}"
                except:
                    error_msg += f" - {response.text[:200]}"
                self.log_test(test_name, "FAIL", error_msg)
                return None
                
        except Exception as e:
            self.log_test(test_name, "FAIL", str(e))
            return None
    
    async def run_all_tests(self):
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}Starting API Endpoint Tests{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
        
        # 1. Health Check
        print(f"\n{Colors.YELLOW}1. HEALTH CHECK{Colors.RESET}")
        await self.test_endpoint("GET", "/../", "Root endpoint (BASE_URL/)", expected_status=200)
        await self.test_endpoint("GET", "/../health", "Health check endpoint", expected_status=200)
        
        # 2. Authentication Endpoints
        print(f"\n{Colors.YELLOW}2. AUTHENTICATION ENDPOINTS{Colors.RESET}")
        
        # 2.1 Password Strength Check
        result = await self.test_endpoint(
            "POST", "/auth/check-password-strength",
            "Check password strength",
            data={"password": "WeakPass"},
            expected_status=200
        )
        
        # 2.2 User Registration
        result = await self.test_endpoint(
            "POST", "/auth/register",
            "Register new user",
            data={
                "email": f"testuser{self.timestamp}@example.com",
                "password": "TestPassword123!",
                "name": "Test User",
                "phone": "+1234567890"
            },
            expected_status=201  # 201 Created is the correct status for user creation
        )
        
        if result:
            self.test_data['user_id'] = result.get('id')
            self.test_data['user_email'] = result.get('email')
        
        # 2.3 Duplicate Registration (should fail)
        await self.test_endpoint(
            "POST", "/auth/register",
            "Duplicate registration (should fail)",
            data={
                "email": f"testuser{self.timestamp}@example.com",
                "password": "TestPassword123!",
                "name": "Test User",
                "phone": "+1234567890"
            },
            expected_status=400
        )
        
        # 2.4 Login with unverified email (should fail or return warning)
        result = await self.test_endpoint(
            "POST", "/auth/login",
            "Login with unverified email",
            data={
                "email": f"testuser{self.timestamp}@example.com",
                "password": "TestPassword123!"
            },
            expected_status=401  # Assuming unverified users can't login
        )
        
        # 2.5 Register another user for verification test
        result = await self.test_endpoint(
            "POST", "/auth/register",
            "Register second user",
            data={
                "email": f"verified{self.timestamp}@example.com",
                "password": "VerifiedPass123!",
                "name": "Verified User",
                "phone": "+9876543210"
            },
            expected_status=201  # 201 Created is the correct status for user creation
        )
        
        # 2.6 Forgot Password
        await self.test_endpoint(
            "POST", "/auth/forgot-password",
            "Forgot password request",
            data={"email": f"testuser{self.timestamp}@example.com"},
            expected_status=200
        )
        
        # 2.7 MFA Setup (requires auth - will test later)
        
        # 3. Token Endpoints (without auth)
        print(f"\n{Colors.YELLOW}3. TOKEN ENDPOINTS (Unauthenticated){Colors.RESET}")
        
        await self.test_endpoint(
            "POST", "/auth/refresh",
            "Refresh token (no token - should fail)",
            data={"refresh_token": "invalid-token"},
            expected_status=401
        )
        
        # 4. User Management (will need auth)
        print(f"\n{Colors.YELLOW}4. USER MANAGEMENT{Colors.RESET}")
        print(f"  {Colors.YELLOW}Note: These endpoints require authentication{Colors.RESET}")
        
        # Test without auth (should fail with 403 - no credentials provided)
        await self.test_endpoint(
            "GET", "/users/me",
            "Get current user (no auth - should fail)",
            expected_status=403  # 403 when no Authorization header is provided
        )
        
        await self.test_endpoint(
            "GET", "/users",
            "List users (no auth - should fail)",
            expected_status=403  # 403 when no Authorization header is provided
        )
        
        # 5. Print Summary
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
        
        return self.failed == 0

async def main():
    tester = APITester()
    try:
        success = await tester.run_all_tests()
        if success:
            print(f"{Colors.GREEN}All tests passed!{Colors.RESET}")
            return 0
        else:
            print(f"{Colors.RED}Some tests failed. See details above.{Colors.RESET}")
            return 1
    finally:
        await tester.close()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
