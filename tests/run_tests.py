#!/usr/bin/env python3
import unittest
import sys
import os
import subprocess

# Add parent directory to path to import test modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_header(title):
    """Print a formatted header for test sections"""
    separator = "=" * 70
    print(f"\n{separator}")
    print(f"    {title}")
    print(f"{separator}\n")

def run_container_builds():
    """Build all Docker containers required for tests"""
    print_header("Building Docker Containers")

    containers = [
        "data_cleaning",
        "sentiment_analysis",
        "text_summarization"
    ]

    for container in containers:
        print(f"Building container: {container}")
        try:
            subprocess.run(
                ["docker", "build", "-t", f"ai-orchestrator/{container.replace('_', '-')}",
                 f"containers/{container}/"],
                check=True,
                capture_output=True
            )
            print(f"✅ Successfully built container: {container}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build container {container}: {e}")
            print(f"STDOUT: {e.stdout.decode('utf-8')}")
            print(f"STDERR: {e.stderr.decode('utf-8')}")
            return False

    return True

def run_test_suite():
    """Run all test suites"""
    # Import test modules
    from tests.test_containers import TestContainers
    from tests.test_llm_integration import TestLLMIntegration
    from tests.test_orchestrator import TestOrchestrator
    from tests.test_app import TestFlaskApp

    # Create test suites
    loader = unittest.TestLoader()

    # Load from each test module
    suites = [
        loader.loadTestsFromTestCase(TestContainers),
        loader.loadTestsFromTestCase(TestLLMIntegration),
        loader.loadTestsFromTestCase(TestOrchestrator),
        loader.loadTestsFromTestCase(TestFlaskApp)
    ]

    # Combine all suites
    all_tests = unittest.TestSuite(suites)

    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(all_tests).wasSuccessful()

if __name__ == "__main__":
    print_header("AI Orchestrator with Containers - Test Suite")

    # Ensure containers are built first
    if not run_container_builds():
        print("❌ Container build failed. Cannot proceed with tests.")
        sys.exit(1)

    # Run all tests
    success = run_test_suite()

    # Exit with appropriate code
    sys.exit(0 if success else 1)