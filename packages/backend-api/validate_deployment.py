#!/usr/bin/env python3
"""
Comprehensive deployment validation script.
This script validates that the backend API is ready for deployment.
"""

import sys
import os
from pathlib import Path

# Add backend-api directory to path
sys.path.insert(0, str(Path(__file__).parent))

def validate_imports():
    """Test that all modules can be imported without errors."""
    print("=" * 60)
    print("STEP 1: Validating module imports...")
    print("=" * 60)

    modules_to_test = [
        "dependencies",
        "auth",
        "shared.key_vault_client",
        "api.health",
        "api.feedback",
        "api.users",
        "api.auth",
        "api.articles",
        "api.topics",
        "api.chat",
        "api.analytics",
        "api.user_articles",
        "api.rss_feeds",
    ]

    failed_imports = []

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except Exception as e:
            print(f"✗ {module_name}: {str(e)}")
            failed_imports.append((module_name, str(e)))

    if failed_imports:
        print("\n❌ IMPORT VALIDATION FAILED")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    else:
        print("\n✅ All imports successful!")
        return True


def validate_app_initialization():
    """Test that FastAPI app can be initialized."""
    print("\n" + "=" * 60)
    print("STEP 2: Validating FastAPI app initialization...")
    print("=" * 60)

    try:
        from main import app
        print(f"✓ App created: {app.title}")
        print(f"✓ Version: {app.version}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize app: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def validate_routes():
    """Test that all routes are properly registered."""
    print("\n" + "=" * 60)
    print("STEP 3: Validating route registration...")
    print("=" * 60)

    try:
        from main import app

        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                for method in route.methods:
                    if method != 'HEAD':  # Skip HEAD methods
                        routes.append(f"{method:7s} {route.path}")

        # Expected critical routes
        expected_routes = [
            "/api/health",
            "/api/feedback",
            "/api/users",
            "/api/articles",
            "/api/rss_feeds",
            "/api/topics/suggest",
            "/api/chat",
            "/api/analytics",
        ]

        print(f"\n📋 Total routes registered: {len(routes)}")
        print("\nCritical routes:")

        missing_routes = []
        for expected in expected_routes:
            found = any(expected in route for route in routes)
            if found:
                print(f"  ✓ {expected}")
            else:
                print(f"  ✗ {expected} (MISSING)")
                missing_routes.append(expected)

        if missing_routes:
            print(f"\n❌ Missing {len(missing_routes)} critical routes")
            return False
        else:
            print("\n✅ All critical routes registered!")
            return True

    except Exception as e:
        print(f"✗ Failed to validate routes: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def validate_dependencies():
    """Test that all required dependencies are available."""
    print("\n" + "=" * 60)
    print("STEP 4: Validating dependencies...")
    print("=" * 60)

    required_packages = [
        "fastapi",
        "uvicorn",
        "pymongo",
        "google.genai",
        "azure.identity",
        "azure.keyvault.secrets",
        "dotenv",
        "fastapi_azure_auth",
        "jose",
        "jwt",
        "feedparser",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (NOT INSTALLED)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n❌ Missing {len(missing_packages)} required packages")
        return False
    else:
        print("\n✅ All dependencies available!")
        return True


def validate_function_ordering():
    """Validate that helper functions are defined before use."""
    print("\n" + "=" * 60)
    print("STEP 5: Validating function ordering...")
    print("=" * 60)

    # This is mainly for feedback.py which had the issue
    try:
        from api import feedback

        # Check that helper functions exist and are callable
        assert callable(feedback.get_success_html), "get_success_html must be callable"
        assert callable(feedback.get_error_html), "get_error_html must be callable"

        # Test that they can be called
        test_success = feedback.get_success_html("up")
        test_error = feedback.get_error_html("Test error")

        assert "Thank You" in test_success, "Success HTML should contain 'Thank You'"
        assert "Test error" in test_error, "Error HTML should contain error message"

        print("✓ feedback.py: Helper functions properly ordered")
        print("  ✓ get_success_html() callable and working")
        print("  ✓ get_error_html() callable and working")

        print("\n✅ Function ordering validated!")
        return True

    except Exception as e:
        print(f"✗ Function ordering validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def validate_health_endpoint():
    """Validate that health endpoint structure is correct."""
    print("\n" + "=" * 60)
    print("STEP 6: Validating health endpoint...")
    print("=" * 60)

    try:
        from api import health

        # Check that the route handler exists
        assert hasattr(health, 'health_check'), "health_check function must exist"
        print("✓ Health endpoint handler exists")

        # Verify it's an async function
        import inspect
        assert inspect.iscoroutinefunction(health.health_check), "health_check must be async"
        print("✓ Health endpoint is async")

        print("\n✅ Health endpoint validated!")
        return True

    except Exception as e:
        print(f"✗ Health endpoint validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation checks."""
    print("\n" + "🔍 " * 20)
    print("BACKEND API DEPLOYMENT VALIDATION")
    print("🔍 " * 20 + "\n")

    # Disable Key Vault calls during validation (local testing)
    os.environ.setdefault("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
    os.environ.setdefault("GEMINI_API_KEY", "test-key")
    os.environ.setdefault("ENTRA_TENANT_ID", "test-tenant")
    os.environ.setdefault("ENTRA_CLIENT_ID", "test-client")

    results = {
        "Import Validation": validate_imports(),
        "App Initialization": validate_app_initialization(),
        "Route Registration": validate_routes(),
        "Dependencies": validate_dependencies(),
        "Function Ordering": validate_function_ordering(),
        "Health Endpoint": validate_health_endpoint(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:25s} {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n" + "🎉 " * 20)
        print("ALL VALIDATION CHECKS PASSED!")
        print("Backend API is ready for deployment! 🚀")
        print("🎉 " * 20 + "\n")
        return 0
    else:
        print("\n" + "⚠️  " * 20)
        print("VALIDATION FAILED!")
        print("Please fix the issues above before deploying.")
        print("⚠️  " * 20 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
