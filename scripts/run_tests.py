#!/usr/bin/env python3
"""
Test Runner Script for OMNI-AI
Provides convenient interface for running different test suites
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"\n✓ {description} completed successfully")
    else:
        print(f"\n✗ {description} failed with return code {result.returncode}")
    
    return result.returncode == 0


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests only."""
    cmd = ["pytest", "-m", "unit"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests only."""
    cmd = ["pytest", "-m", "integration"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    return run_command(cmd, "Integration Tests")


def run_performance_tests(verbose=False):
    """Run performance tests only."""
    cmd = ["pytest", "-m", "performance", "-s"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Performance Tests")


def run_all_tests(verbose=False, coverage=False):
    """Run all tests."""
    cmd = ["pytest"]
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    return run_command(cmd, "All Tests")


def run_specific_test(test_file, verbose=False):
    """Run a specific test file."""
    cmd = ["pytest", test_file]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Specific Test: {test_file}")


def run_test_with_pattern(pattern, verbose=False):
    """Run tests matching a pattern."""
    cmd = ["pytest", "-k", pattern]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Tests matching pattern: {pattern}")


def generate_coverage_report():
    """Generate coverage report."""
    cmd = ["pytest", "--cov=src", "--cov-report=html", "--cov-report=term-missing"]
    return run_command(cmd, "Coverage Report")


def main():
    parser = argparse.ArgumentParser(
        description="Test Runner for OMNI-AI Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --integration      # Run integration tests only
  python run_tests.py --performance      # Run performance tests only
  python run_tests.py --coverage         # Run tests with coverage report
  python run_tests.py --file tests/test_core_components.py  # Run specific file
  python run_tests.py --pattern "memory" # Run tests matching pattern
  python run_tests.py --verbose          # Run with verbose output
        """
    )
    
    parser.add_argument(
        "--unit", "-u",
        action="store_true",
        help="Run unit tests only"
    )
    
    parser.add_argument(
        "--integration", "-i",
        action="store_true",
        help="Run integration tests only"
    )
    
    parser.add_argument(
        "--performance", "-p",
        action="store_true",
        help="Run performance tests only"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Run specific test file"
    )
    
    parser.add_argument(
        "--pattern", "-k",
        type=str,
        help="Run tests matching pattern"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    if project_root != Path.cwd():
        print(f"Changing directory to project root: {project_root}")
        import os
        os.chdir(project_root)
    
    # Determine which tests to run
    success = True
    
    if args.file:
        success = run_specific_test(args.file, args.verbose)
    elif args.pattern:
        success = run_test_with_pattern(args.pattern, args.verbose)
    elif args.unit:
        success = run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.performance:
        success = run_performance_tests(args.verbose)
    elif args.coverage:
        success = generate_coverage_report()
    else:
        # Run all tests
        success = run_all_tests(args.verbose, args.coverage)
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✓ All tests completed successfully!")
    else:
        print("✗ Some tests failed. Please check the output above.")
    print(f"{'='*60}\n")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()