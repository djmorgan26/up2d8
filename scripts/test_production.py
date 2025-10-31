#!/usr/bin/env python3
"""
UP2D8 Production Testing Script
Tests all major features of the UP2D8 application deployed on Azure
"""

import requests
import json
import time
from typing import Dict, Optional

# Configuration
API_BASE_URL = "https://up2d8.azurewebsites.net"
TEST_USER_EMAIL = "davidjmorgan26@gmail.com"
TEST_USER_PASSWORD = "password12345"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test(test_name: str):
    """Print test header"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")


def test_health_check() -> bool:
    """Test health check endpoint"""
    print_test("Health Check")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        response.raise_for_status()
        data = response.json()

        print_success(f"API is healthy: {data['status']}")
        print_info(f"Service: {data['service']} v{data['version']}")
        print_info(f"Environment: {data['environment']}")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_login() -> Optional[str]:
    """Test user login and return access token"""
    print_test("User Authentication")

    try:
        # Test login
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        print_success("Login successful")
        print_info(f"User: {data['user']['full_name']} ({data['user']['email']})")
        print_info(f"User ID: {data['user']['id']}")
        print_info(f"Tier: {data['user']['tier']}")
        print_info(f"Token expires in: {data['expires_in']} seconds")

        return data['access_token']
    except Exception as e:
        print_error(f"Login failed: {e}")
        return None


def test_sync_sources(token: str) -> bool:
    """Test syncing sources from YAML to database"""
    print_test("Sync Sources from Config")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/scraping/sources/sync/direct",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        print_success("Sources synced successfully")
        print_info(f"Sources created: {data['sources_created']}")
        print_info(f"Sources updated: {data['sources_updated']}")
        print_info(f"Total sources: {data['total_sources']}")
        return True
    except Exception as e:
        print_error(f"Source sync failed: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return False


def test_list_sources(token: str) -> bool:
    """Test listing sources"""
    print_test("List Content Sources")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/scraping/sources",
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        sources = response.json()

        print_success(f"Found {len(sources)} sources")

        # Display first few sources
        for i, source in enumerate(sources[:5]):
            print_info(f"{i+1}. {source['name']} ({source['type']}) - Priority: {source['priority']}")
            print(f"   URL: {source['url']}")
            print(f"   Industries: {', '.join(source.get('industries', []))}")

        if len(sources) > 5:
            print_info(f"... and {len(sources) - 5} more sources")

        return True
    except Exception as e:
        print_error(f"Failed to list sources: {e}")
        return False


def test_scrape_source(token: str, source_id: str = "techcrunch_ai") -> bool:
    """Test scraping a specific source"""
    print_test(f"Scrape Source: {source_id}")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        print_info("Starting scraping... (this may take 10-30 seconds)")

        response = requests.post(
            f"{API_BASE_URL}/api/v1/scraping/scrape/{source_id}/direct",
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

        print_success(f"Scraping completed: {data['message']}")
        print_info(f"Articles scraped: {data['articles_scraped']}")
        print_info(f"Articles stored: {data['articles_stored']}")
        print_info(f"Duplicates found: {data['duplicates_found']}")
        return True
    except Exception as e:
        print_error(f"Scraping failed: {e}")
        if hasattr(e, 'response'):
            try:
                error_data = e.response.json()
                print_error(f"Details: {error_data.get('detail', e.response.text)}")
            except:
                print_error(f"Response: {e.response.text[:200]}")
        return False


def test_list_articles(token: str) -> bool:
    """Test listing scraped articles"""
    print_test("List Scraped Articles")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/scraping/articles?limit=10",
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        articles = response.json()

        print_success(f"Found {len(articles)} recent articles")

        # Display first few articles
        for i, article in enumerate(articles[:5]):
            print_info(f"{i+1}. {article['title']}")
            print(f"   Source: {article['source_id']}")
            print(f"   URL: {article['source_url']}")
            print(f"   Status: {article['processing_status']}")
            print(f"   Industries: {', '.join(article.get('industries', []))}")

        if len(articles) > 5:
            print_info(f"... and {len(articles) - 5} more articles")

        return True
    except Exception as e:
        print_error(f"Failed to list articles: {e}")
        return False


def test_article_stats(token: str) -> bool:
    """Test getting article statistics"""
    print_test("Article Statistics")

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE_URL}/api/v1/scraping/articles/stats",
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        stats = response.json()

        print_success("Retrieved article statistics")
        print_info(f"Total articles: {stats['total_articles']}")

        if stats.get('by_status'):
            print_info("Articles by status:")
            for status, count in stats['by_status'].items():
                print(f"   {status}: {count}")

        if stats.get('top_sources'):
            print_info("Top sources:")
            for source_info in stats['top_sources'][:5]:
                print(f"   {source_info['source']}: {source_info['count']} articles")

        return True
    except Exception as e:
        print_error(f"Failed to get article stats: {e}")
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}UP2D8 Production Testing Suite{Colors.END}")
    print(f"{Colors.BLUE}Testing API at: {API_BASE_URL}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    results = {}

    # Test 1: Health check
    results['health'] = test_health_check()
    time.sleep(1)

    # Test 2: Login
    token = test_login()
    results['login'] = token is not None

    if not token:
        print_error("\n❌ Cannot proceed without authentication token")
        return results

    time.sleep(1)

    # Test 3: Sync sources
    results['sync_sources'] = test_sync_sources(token)
    time.sleep(1)

    # Test 4: List sources
    results['list_sources'] = test_list_sources(token)
    time.sleep(1)

    # Test 5: Scrape a source
    results['scrape'] = test_scrape_source(token, "techcrunch_ai")
    time.sleep(1)

    # Test 6: List articles
    results['list_articles'] = test_list_articles(token)
    time.sleep(1)

    # Test 7: Article statistics
    results['article_stats'] = test_article_stats(token)

    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{test_name.replace('_', ' ').title()}: {status}")

    print(f"\n{Colors.BLUE}Overall: {passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print(f"{Colors.GREEN}🎉 All tests passed! UP2D8 is working correctly.{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  Some tests failed. Check the output above for details.{Colors.END}")

    return results


if __name__ == "__main__":
    results = run_all_tests()
    exit(0 if all(results.values()) else 1)
