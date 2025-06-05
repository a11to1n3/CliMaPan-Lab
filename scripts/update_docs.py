#!/usr/bin/env python3
"""
Script to update documentation automatically.
This script can be run locally or as part of CI/CD to ensure documentation is up to date.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, text=True, check=check
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def build_docs(docs_dir, clean=False):
    """Build the documentation using Sphinx."""
    print("Building documentation...")

    if clean:
        print("Cleaning previous build...")
        run_command("make clean", cwd=docs_dir, check=False)

    # Build HTML documentation
    result = run_command("sphinx-build -W -b html . _build/html", cwd=docs_dir)

    if result.returncode == 0:
        print("✅ Documentation built successfully!")
        return True
    else:
        print("❌ Documentation build failed!")
        return False


def check_links(docs_dir):
    """Check for broken links in documentation."""
    print("Checking documentation links...")
    result = run_command(
        "sphinx-build -W -b linkcheck . _build/linkcheck", cwd=docs_dir, check=False
    )

    if result.returncode == 0:
        print("✅ All links are working!")
    else:
        print("⚠️  Some links may be broken (check _build/linkcheck/output.txt)")


def update_api_docs(project_root):
    """Update API documentation using sphinx-apidoc."""
    print("Updating API documentation...")

    api_dir = project_root / "docs" / "api"
    source_dir = project_root / "climapan_lab"

    # Generate API documentation
    result = run_command(
        f"sphinx-apidoc -f -o {api_dir} {source_dir}", cwd=project_root, check=False
    )

    if result.returncode == 0:
        print("✅ API documentation updated!")
    else:
        print("⚠️  API documentation update had issues")


def trigger_rtd_build(webhook_url=None):
    """Trigger a Read the Docs build via webhook."""
    if not webhook_url:
        webhook_url = os.environ.get("RTD_WEBHOOK_URL")

    if not webhook_url:
        print("⚠️  No Read the Docs webhook URL provided")
        return False

    print("Triggering Read the Docs build...")

    try:
        response = requests.post(
            webhook_url,
            json={"branches": ["main"]},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            print("✅ Read the Docs build triggered successfully!")
            return True
        else:
            print(f"⚠️  Read the Docs build trigger failed: {response.status_code}")
            return False

    except requests.RequestException as e:
        print(f"❌ Error triggering Read the Docs build: {e}")
        return False


def check_docstring_coverage(project_root):
    """Check docstring coverage using interrogate."""
    print("Checking docstring coverage...")

    source_dir = project_root / "climapan_lab"

    result = run_command(
        f"interrogate {source_dir} --ignore-init-method --ignore-magic --fail-under=50 --verbose",
        cwd=project_root,
        check=False,
    )

    # Generate badge
    run_command(
        f"interrogate {source_dir} --ignore-init-method --ignore-magic --generate-badge docs/_static/",
        cwd=project_root,
        check=False,
    )

    if result.returncode == 0:
        print("✅ Docstring coverage is adequate!")
    else:
        print("⚠️  Docstring coverage could be improved")


def main():
    parser = argparse.ArgumentParser(description="Update CliMaPan-Lab documentation")
    parser.add_argument(
        "--clean", action="store_true", help="Clean build directory first"
    )
    parser.add_argument(
        "--check-links", action="store_true", help="Check for broken links"
    )
    parser.add_argument(
        "--update-api", action="store_true", help="Update API documentation"
    )
    parser.add_argument(
        "--trigger-rtd", action="store_true", help="Trigger Read the Docs build"
    )
    parser.add_argument(
        "--check-coverage", action="store_true", help="Check docstring coverage"
    )
    parser.add_argument("--webhook-url", type=str, help="Read the Docs webhook URL")
    parser.add_argument("--all", action="store_true", help="Run all update steps")

    args = parser.parse_args()

    # Get project root directory
    project_root = Path(__file__).parent.parent.absolute()
    docs_dir = project_root / "docs"

    print(f"Project root: {project_root}")
    print(f"Documentation directory: {docs_dir}")

    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        sys.exit(1)

    success = True

    # Update API documentation if requested
    if args.update_api or args.all:
        update_api_docs(project_root)

    # Check docstring coverage if requested
    if args.check_coverage or args.all:
        check_docstring_coverage(project_root)

    # Build documentation
    if not build_docs(docs_dir, clean=args.clean):
        success = False

    # Check links if requested
    if args.check_links or args.all:
        check_links(docs_dir)

    # Trigger Read the Docs build if requested
    if args.trigger_rtd or args.all:
        if not trigger_rtd_build(args.webhook_url):
            success = False

    if success:
        print("\n🎉 Documentation update completed successfully!")
        print(f"📖 Local docs available at: file://{docs_dir}/_build/html/index.html")
        print(
            "🌐 Online docs should be available at: https://climapan-lab.readthedocs.io/"
        )
    else:
        print("\n❌ Documentation update completed with some errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
