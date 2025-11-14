#!/usr/bin/env python3
"""
End-to-end test for newsletter generation system.
Tests both database state and function execution.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime
import json

# Add the project root to sys.path to enable module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymongo
from shared.key_vault_client import get_secret_client


class NewsletterTester:
    def __init__(self):
        load_dotenv()
        self.test_results = []
        self.test_email = None
        self.function_url = None
        self.function_key = None

    def log_test(self, test_name, passed, message=""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")

    def test_database_connection(self):
        """Test 1: Connect to Cosmos DB."""
        try:
            secret_client = get_secret_client()
            cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
            client = pymongo.MongoClient(cosmos_db_connection_string)
            db = client.up2d8

            # Test connection
            db.command('ping')
            self.db = db
            self.log_test("Database Connection", True, "Connected to Cosmos DB")
            return True
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False

    def test_user_exists(self):
        """Test 2: Check if test user exists with correct settings."""
        try:
            users_collection = self.db.users
            user = users_collection.find_one({"email": self.test_email})

            if not user:
                self.log_test("User Exists", False, f"User {self.test_email} not found")
                return False

            # Check user settings
            topics = user.get('topics', [])
            prefs = user.get('preferences', {})
            email_notif = prefs.get('email_notifications', True)
            frequency = prefs.get('newsletter_frequency', 'daily')

            issues = []
            if not topics:
                issues.append("No topics configured")
            if not email_notif:
                issues.append("Email notifications disabled")
            if frequency != 'daily':
                issues.append(f"Frequency set to '{frequency}'")

            if issues:
                self.log_test("User Settings", False, "; ".join(issues))
                return False

            self.log_test("User Settings", True,
                         f"Topics: {len(topics)}, Notifications: {email_notif}, Frequency: {frequency}")
            return True

        except Exception as e:
            self.log_test("User Exists", False, str(e))
            return False

    def test_articles_available(self):
        """Test 3: Check if unprocessed articles exist."""
        try:
            articles_collection = self.db.articles
            total = articles_collection.count_documents({})
            unprocessed = articles_collection.count_documents({"processed": False})

            if total == 0:
                self.log_test("Articles Available", False, "No articles in database")
                return False

            if unprocessed == 0:
                self.log_test("Articles Available", False,
                            f"{total} articles exist but all are processed")
                return False

            self.log_test("Articles Available", True,
                         f"{unprocessed} unprocessed out of {total} total")
            return True

        except Exception as e:
            self.log_test("Articles Available", False, str(e))
            return False

    def test_articles_match_topics(self):
        """Test 4: Check if articles match user topics."""
        try:
            users_collection = self.db.users
            articles_collection = self.db.articles

            user = users_collection.find_one({"email": self.test_email})
            topics = user.get('topics', [])
            articles = list(articles_collection.find({"processed": False}))

            matching_articles = [
                a for a in articles
                if any(topic.lower() in a.get('title', '').lower() or
                       topic.lower() in a.get('summary', '').lower()
                       for topic in topics)
            ]

            if not matching_articles:
                self.log_test("Articles Match Topics", False,
                            f"No articles match topics: {topics}")
                return False

            self.log_test("Articles Match Topics", True,
                         f"{len(matching_articles)} articles match user topics")
            return True

        except Exception as e:
            self.log_test("Articles Match Topics", False, str(e))
            return False

    def test_manual_trigger(self):
        """Test 5: Trigger newsletter generation manually."""
        try:
            if not self.function_url or not self.function_key:
                self.log_test("Manual Trigger", False,
                            "Function URL or key not provided (skipping)")
                return False

            url = f"{self.function_url}?code={self.function_key}&email={self.test_email}"

            print(f"    Calling: {self.function_url}")
            response = requests.get(url, timeout=120)  # 2 minute timeout

            if response.status_code != 200:
                self.log_test("Manual Trigger", False,
                            f"HTTP {response.status_code}: {response.text[:200]}")
                return False

            result = response.json()
            newsletters_sent = result.get('newsletters_sent', 0)

            if newsletters_sent == 0:
                details = result.get('details', {})
                skipped = details.get('skipped', [])
                errors = details.get('errors', [])

                msg = f"No newsletters sent. Skipped: {len(skipped)}, Errors: {len(errors)}"
                if skipped:
                    msg += f"\n    Skipped reasons: {[s.get('reason') for s in skipped]}"
                if errors:
                    msg += f"\n    Errors: {[e.get('error') for e in errors]}"

                self.log_test("Manual Trigger", False, msg)
                return False

            self.log_test("Manual Trigger", True,
                         f"Newsletter sent to {newsletters_sent} user(s)")

            # Save response for inspection
            print("\n    Full Response:")
            print(f"    {json.dumps(result, indent=4)}\n")

            return True

        except requests.exceptions.Timeout:
            self.log_test("Manual Trigger", False, "Request timed out after 120s")
            return False
        except Exception as e:
            self.log_test("Manual Trigger", False, str(e))
            return False

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")

        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   - {result['test']}")
                    if result['message']:
                        print(f"     {result['message']}")

        print("\n" + "=" * 80)

        return failed == 0

    def run(self):
        """Run all tests."""
        print("=" * 80)
        print("NEWSLETTER END-TO-END TEST")
        print("=" * 80)
        print()

        # Get test parameters
        self.test_email = input("Enter test email address: ").strip()
        if not self.test_email:
            print("❌ Email is required")
            return False

        print("\nOptional: Test manual trigger endpoint")
        print("(Leave blank to skip manual trigger test)")
        self.function_url = input("Function URL (e.g., https://xxx.azurewebsites.net/api/NewsletterGeneratorManual): ").strip()

        if self.function_url:
            self.function_key = input("Function Key: ").strip()

        print("\n" + "=" * 80)
        print("RUNNING TESTS")
        print("=" * 80)
        print()

        # Run tests in order
        if not self.test_database_connection():
            print("\n❌ Cannot continue - database connection failed")
            return False

        self.test_user_exists()
        self.test_articles_available()
        self.test_articles_match_topics()

        if self.function_url and self.function_key:
            self.test_manual_trigger()

        # Print summary
        success = self.print_summary()

        if success:
            print("\n✅ ALL TESTS PASSED!")
            print("\nYou should receive an email at:", self.test_email)
            print("If you ran the manual trigger test, check your inbox in 1-2 minutes.")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("\nRecommendations:")
            print("1. Run setup_test_data.py to configure test data")
            print("2. Check DEBUG_DAILY_DIGEST.md for troubleshooting")
            print("3. Verify Azure Function is deployed and running")

        return success


if __name__ == "__main__":
    tester = NewsletterTester()
    success = tester.run()
    sys.exit(0 if success else 1)
