#!/usr/bin/env python3
"""
Deployment Verification Script for UP2D8 Azure Static Web App (Asher)

This script helps verify that the latest frontend code is deployed to production.
It checks for specific features that should be present in the deployed version.
"""

import sys
import json
import subprocess
from datetime import datetime

# Frontend URL
FRONTEND_URL = "https://gray-wave-00bdfc60f.3.azurestaticapps.net"

# Expected features in the latest deployment
EXPECTED_FEATURES = {
    "topic_categories": {
        "file": "packages/web-app/src/lib/constants.ts",
        "description": "12 predefined topic categories (Technology, Health, Business, etc.)",
        "commit": "4139d8c",
        "indicators": [
            "TOPIC_CATEGORIES",
            "Technology",
            "Health",
            "Business"
        ]
    },
    "preferences_dialog": {
        "file": "packages/web-app/src/components/PreferencesDialog.tsx",
        "description": "Multi-select gallery UI for topic preferences",
        "commit": "4139d8c",
        "indicators": [
            "multi-select gallery",
            "predefined categories"
        ]
    }
}

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_section(text):
    """Print a formatted section header"""
    print(f"\n--- {text} ---\n")

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"

def check_git_status():
    """Check git repository status"""
    print_section("Git Repository Status")

    # Current branch
    returncode, stdout, _ = run_command("git rev-parse --abbrev-ref HEAD")
    current_branch = stdout.strip()
    print(f"Current branch: {current_branch}")

    # Latest commit
    returncode, stdout, _ = run_command("git log -1 --oneline")
    latest_commit = stdout.strip()
    print(f"Latest commit: {latest_commit}")

    # Check if on main
    if current_branch == "main":
        print("✅ On main branch - changes here will auto-deploy on push")
    else:
        print(f"⚠️  On feature branch - merge to main for deployment")

    return current_branch

def check_main_branch_commits():
    """Check what's on the main branch"""
    print_section("Main Branch Status")

    # Ensure we have latest main
    print("Fetching latest from origin/main...")
    run_command("git fetch origin main 2>&1")

    # Show recent commits on main
    returncode, stdout, _ = run_command("git log origin/main --oneline -5 -- packages/web-app/")
    print("Recent frontend commits on main:")
    print(stdout if stdout else "No recent commits found")

    # Compare current branch with main
    returncode, stdout, _ = run_command("git diff origin/main HEAD --stat")
    if stdout.strip():
        print("\n⚠️  Current branch differs from main:")
        print(stdout)
    else:
        print("\n✅ Current branch is in sync with main")

def check_expected_features():
    """Check if expected features exist in the codebase"""
    print_section("Expected Features in Codebase")

    all_present = True
    for feature_name, feature_info in EXPECTED_FEATURES.items():
        print(f"\nChecking: {feature_info['description']}")
        print(f"  File: {feature_info['file']}")
        print(f"  Commit: {feature_info['commit']}")

        # Check if file exists and contains indicators
        try:
            with open(feature_info['file'], 'r') as f:
                content = f.read()
                found_indicators = []
                missing_indicators = []

                for indicator in feature_info['indicators']:
                    if indicator.lower() in content.lower():
                        found_indicators.append(indicator)
                    else:
                        missing_indicators.append(indicator)

                if missing_indicators:
                    print(f"  ⚠️  Missing indicators: {', '.join(missing_indicators)}")
                    all_present = False
                else:
                    print(f"  ✅ All indicators found")
        except FileNotFoundError:
            print(f"  ❌ File not found!")
            all_present = False

    return all_present

def check_frontend_accessibility():
    """Check if frontend is accessible"""
    print_section("Frontend Accessibility Check")

    print(f"Testing: {FRONTEND_URL}")

    # Try to access the frontend
    returncode, stdout, stderr = run_command(f"curl -s -o /dev/null -w '%{{http_code}}' {FRONTEND_URL}")
    http_code = stdout.strip()

    print(f"HTTP Status: {http_code}")

    if http_code == "200":
        print("✅ Frontend is accessible")
        return True
    elif http_code == "403":
        print("⚠️  Frontend returned 403 Forbidden")
        print("   This could indicate:")
        print("   - Azure access restrictions (IP allowlist)")
        print("   - Authentication requirements")
        print("   - Network/firewall issues")
        print("\n   ACTION: Check Azure Portal for access policies")
        return False
    else:
        print(f"❌ Frontend returned unexpected status: {http_code}")
        return False

def check_github_actions():
    """Check for recent GitHub Actions deployments"""
    print_section("GitHub Actions Deployment Status")

    print("To check GitHub Actions deployment status:")
    print(f"1. Visit: https://github.com/djmorgan26/up2d8/actions/workflows/up2d8-web.yml")
    print("2. Look for the most recent 'Deploy Static Web App' workflow run")
    print("3. Check if it succeeded and when it ran")
    print("4. Verify it deployed the latest commits from main branch")
    print("\nAlternatively, use GitHub CLI if available:")
    print("  gh run list --workflow=up2d8-web.yml --limit 5")

def provide_recommendations():
    """Provide recommendations based on findings"""
    print_section("Recommendations")

    print("To verify your deployment is up-to-date:")
    print("\n1. Check GitHub Actions:")
    print("   - Go to: https://github.com/djmorgan26/up2d8/actions")
    print("   - Find the 'Deploy Static Web App' workflow")
    print("   - Verify it ran successfully after your latest commit to main")

    print("\n2. Manual Deployment (if needed):")
    print("   - Go to: https://github.com/djmorgan26/up2d8/actions")
    print("   - Select 'Deploy Static Web App' workflow")
    print("   - Click 'Run workflow'")
    print("   - Select 'main' branch and click 'Run workflow'")

    print("\n3. Check Azure Portal:")
    print("   - Go to: https://portal.azure.com")
    print("   - Find your Static Web App resource")
    print("   - Check deployment history and access policies")
    print("   - Look for any access restrictions (IP allowlists, etc.)")

    print("\n4. Verify from Browser:")
    print("   - Open: https://gray-wave-00bdfc60f.3.azurestaticapps.net")
    print("   - If you can access it, check if the following features exist:")
    print("     • Topic preferences should show 12 predefined categories")
    print("     • Categories: Technology, Health, Business, Science, etc.")
    print("     • Multi-select gallery UI with checkboxes")

    print("\n5. Check Build Output Locally:")
    print("   cd packages/web-app")
    print("   npm install")
    print("   npm run build")
    print("   # Check that dist/ folder is created successfully")

def main():
    """Main verification routine"""
    print_header("UP2D8 Deployment Verification")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check git status
    current_branch = check_git_status()

    # Check main branch
    check_main_branch_commits()

    # Check expected features
    features_present = check_expected_features()

    # Check frontend accessibility
    frontend_accessible = check_frontend_accessibility()

    # Check GitHub Actions
    check_github_actions()

    # Provide recommendations
    provide_recommendations()

    # Final summary
    print_header("Summary")

    if features_present:
        print("✅ Expected features present in codebase")
    else:
        print("❌ Some expected features missing in codebase")

    if frontend_accessible:
        print("✅ Frontend is accessible")
    else:
        print("⚠️  Frontend accessibility issues detected")

    if current_branch != "main":
        print(f"\n⚠️  You're on branch '{current_branch}', not 'main'")
        print("   Merge to main to trigger automatic deployment")

    print("\n" + "="*70)
    print("\nFor deployment issues, check:")
    print("1. GitHub Actions workflow runs")
    print("2. Azure Portal for access restrictions")
    print("3. Ensure you're testing from an allowed IP/location")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
