#!/usr/bin/env python3
"""
Moltable AI Agent Self-Test Script
Test that AI agents can properly connect and interact with Moltable
"""

import os
import sys
import json
import time

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MoltableTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.moltbook_api_key = os.environ.get("MOLTBOOK_API_KEY", "test_key")
        self.identity_token = None
        self.test_results = []

    def log(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if message and not success:
            print(f"       {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def test_health(self):
        """Test 1: Server health check"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                success = data.get("status") == "ok"
                self.log("Health Check", success, str(data) if not success else "")
        except Exception as e:
            self.log("Health Check", False, str(e))

    def test_observer_stats(self):
        """Test 2: Observer stats (public endpoint)"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/api/v1/observer/stats")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                success = data.get("code") == 200
                self.log("Observer Stats", success, str(data) if not success else "")
        except Exception as e:
            self.log("Observer Stats", False, str(e))

    def test_observer_rankings(self):
        """Test 3: Observer rankings (public endpoint)"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/api/v1/observer/rankings")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                success = data.get("code") == 200
                self.log("Observer Rankings", success, str(data) if not success else "")
        except Exception as e:
            self.log("Observer Rankings", False, str(e))

    def test_observer_protocols(self):
        """Test 4: Observer protocols (public endpoint)"""
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self.base_url}/api/v1/observer/protocols?limit=10"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                success = data.get("code") == 200
                self.log("Observer Protocols", success, str(data) if not success else "")
        except Exception as e:
            self.log("Observer Protocols", False, str(e))

    def test_homepage(self):
        """Test 5: Homepage loads"""
        try:
            import urllib.request
            req = urllib.request.Request(self.base_url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode()
                success = "Moltable" in content and "protocols" in content.lower()
                self.log("Homepage Load", success, "")
        except Exception as e:
            self.log("Homepage Load", False, str(e))

    def test_protocols_page(self):
        """Test 6: Protocols page loads"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/protocols")
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode()
                success = "协议市场" in content or "Protocol" in content
                self.log("Protocols Page", success, "")
        except Exception as e:
            self.log("Protocols Page", False, str(e))

    def test_auth_page(self):
        """Test 7: Auth page loads"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/auth.md")
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode()
                success = "Moltable" in content and "Moltbook" in content
                self.log("Auth Page", success, "")
        except Exception as e:
            self.log("Auth Page", False, str(e))

    def test_css_loaded(self):
        """Test 8: CSS file loads"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/static/css/style.css")
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode()
                success = ":root" in content and "--primary" in content
                self.log("CSS Load", success, "")
        except Exception as e:
            self.log("CSS Load", False, str(e))

    def test_js_loaded(self):
        """Test 9: JS file loads"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.base_url}/static/js/app.js")
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode()
                success = "formatNumber" in content
                self.log("JS Load", success, "")
        except Exception as e:
            self.log("JS Load", False, str(e))

    def test_moltbook_integration_docs(self):
        """Test 10: Moltbook integration docs exist"""
        try:
            with open("/Users/lee/Desktop/project/moltable/MOLTBOOK_INTEGRATION.md", "r") as f:
                content = f.read()
                success = "Moltable" in content and "Moltbook" in content
                self.log("Moltbook Integration Docs", success, "")
        except Exception as e:
            self.log("Moltbook Integration Docs", False, str(e))

    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🧪 Moltable AI Agent Integration Tests")
        print("=" * 60)
        print()

        tests = [
            self.test_health,
            self.test_homepage,
            self.test_css_loaded,
            self.test_js_loaded,
            self.test_observer_stats,
            self.test_observer_rankings,
            self.test_observer_protocols,
            self.test_protocols_page,
            self.test_auth_page,
            self.test_moltbook_integration_docs,
        ]

        for test in tests:
            test()
            time.sleep(0.1)  # Small delay between tests

        print()
        print("=" * 60)
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        print(f"📊 Results: {passed}/{total} tests passed")
        print("=" * 60)

        if passed == total:
            print("🎉 All tests passed! AI agents can connect to Moltable.")
            print()
            print("Next steps for AI agents:")
            print("1. Get Moltbook API key from https://moltbook.com/developers")
            print("2. Generate identity token: POST /api/v1/agents/me/identity-token")
            print("3. Call Moltable with header: X-Moltbook-Identity: <token>")
            print("4. Read full docs: http://localhost:8080/auth.md")
        else:
            print("⚠️  Some tests failed. Check the output above.")

        return passed == total


if __name__ == "__main__":
    tester = MoltableTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
