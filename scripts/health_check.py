#!/usr/bin/env python3
"""
Production Health Check Monitor for UP2D8

Continuously monitors production services and reports their health status.
Can be run as a cron job or scheduled task for ongoing monitoring.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class HealthChecker:
    """Monitor health of UP2D8 production services."""

    def __init__(self):
        """Initialize health checker with service URLs."""
        self.services = {
            "Backend API": os.getenv("AZURE-BACKEND-APP-URL", "https://up2d8.azurewebsites.net"),
            "Function App": os.getenv("AZURE-FUNCTION-APP-URL", "https://up2d8-function-app.azurewebsites.net/"),
            "Frontend": os.getenv("AZURE-FRONTEND-APP-URL", "https://gray-wave-00bdfc60f.3.azurestaticapps.net"),
        }
        self.timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))

    def check_service(self, name: str, url: str) -> Dict[str, Any]:
        """
        Check health of a single service.

        Args:
            name: Service name
            url: Service URL

        Returns:
            Dictionary with health status and metrics
        """
        result = {
            "name": name,
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "UNKNOWN",
            "response_time": None,
            "status_code": None,
            "error": None,
        }

        try:
            start_time = time.time()
            response = requests.get(url, timeout=self.timeout)
            elapsed_time = time.time() - start_time

            result["response_time"] = round(elapsed_time, 3)
            result["status_code"] = response.status_code

            # Determine health status
            if response.status_code == 200:
                result["status"] = "HEALTHY"
            elif response.status_code in [401, 403]:
                result["status"] = "HEALTHY_AUTH_REQUIRED"
            elif response.status_code == 404:
                result["status"] = "HEALTHY_NO_ROOT"  # Service is up but no root endpoint
            else:
                result["status"] = "DEGRADED"

        except requests.exceptions.Timeout:
            result["status"] = "TIMEOUT"
            result["error"] = f"Request timeout after {self.timeout}s"
        except requests.exceptions.ConnectionError as e:
            result["status"] = "DOWN"
            result["error"] = f"Connection error: {str(e)}"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def check_all_services(self) -> List[Dict[str, Any]]:
        """
        Check health of all services.

        Returns:
            List of health check results
        """
        results = []
        for name, url in self.services.items():
            result = self.check_service(name, url)
            results.append(result)
        return results

    def print_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Print health check results in human-readable format.

        Args:
            results: List of health check results
        """
        print("\n" + "=" * 70)
        print(f"UP2D8 Production Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        for result in results:
            status_icon = self._get_status_icon(result["status"])
            print(f"\n{status_icon} {result['name']}")
            print(f"   URL: {result['url']}")
            print(f"   Status: {result['status']}")

            if result["status_code"]:
                print(f"   HTTP Status: {result['status_code']}")
            if result["response_time"]:
                print(f"   Response Time: {result['response_time']}s")
            if result["error"]:
                print(f"   Error: {result['error']}")

        print("\n" + "=" * 70)
        print(f"Summary: {self._get_summary(results)}")
        print("=" * 70 + "\n")

    def _get_status_icon(self, status: str) -> str:
        """Get emoji icon for status."""
        icons = {
            "HEALTHY": "✅",
            "HEALTHY_AUTH_REQUIRED": "✅",
            "HEALTHY_NO_ROOT": "⚠️",
            "DEGRADED": "⚠️",
            "TIMEOUT": "❌",
            "DOWN": "❌",
            "ERROR": "❌",
            "UNKNOWN": "❓",
        }
        return icons.get(status, "❓")

    def _get_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate summary of health check results."""
        healthy = sum(1 for r in results if r["status"] in ["HEALTHY", "HEALTHY_AUTH_REQUIRED", "HEALTHY_NO_ROOT"])
        total = len(results)

        if healthy == total:
            return f"All {total} services are operational"
        elif healthy > 0:
            return f"{healthy}/{total} services operational, {total - healthy} issues detected"
        else:
            return f"All {total} services are experiencing issues"

    def save_results(self, results: List[Dict[str, Any]], filename: str = None) -> None:
        """
        Save health check results to JSON file.

        Args:
            results: List of health check results
            filename: Output filename (default: health_check_TIMESTAMP.json)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_check_{timestamp}.json"

        output_dir = "health-checks"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w") as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "results": results,
            }, f, indent=2)

        print(f"Results saved to: {filepath}")

    def get_exit_code(self, results: List[Dict[str, Any]]) -> int:
        """
        Get exit code based on health check results.

        Args:
            results: List of health check results

        Returns:
            0 if all services healthy, 1 if any issues
        """
        critical_statuses = ["DOWN", "TIMEOUT", "ERROR"]
        has_critical = any(r["status"] in critical_statuses for r in results)
        return 1 if has_critical else 0


def main():
    """Main entry point for health check script."""
    checker = HealthChecker()

    # Run health check
    results = checker.check_all_services()

    # Print results
    checker.print_results(results)

    # Save results if requested
    if "--save" in sys.argv:
        checker.save_results(results)

    # Exit with appropriate code
    exit_code = checker.get_exit_code(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
