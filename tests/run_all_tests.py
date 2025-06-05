#!/usr/bin/env python3
"""
Comprehensive test runner for CliMaPan-Lab.

This script runs all tests with proper categorization and reporting.
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add the climapan_lab package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import all test modules
from test_basic_functionality import TestBasicFunctionality, TestDataStructures
from test_examples import TestExamples, TestAnalysisScripts
from test_model_components import TestModelComponents, TestParameterStructure, TestErrorHandling
from test_integration import TestIntegrationWorkflows, TestCommandLineInterface, TestDataAnalysisWorkflow, TestErrorRecovery
from test_performance import TestPerformance, TestScalability, TestStressTest


class ColoredTextTestResult(unittest.TextTestResult):
    """Test result class with colored output."""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.verbosity = verbosity
        
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            self.stream.write("\033[92m✓\033[0m ")
            self.stream.write(self.getDescription(test))
            self.stream.write("\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write("\033[91m✗\033[0m ")
            self.stream.write(self.getDescription(test))
            self.stream.write(" (ERROR)\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write("\033[91m✗\033[0m ")
            self.stream.write(self.getDescription(test))
            self.stream.write(" (FAIL)\n")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write("\033[93m⚠\033[0m ")
            self.stream.write(self.getDescription(test))
            self.stream.write(f" (SKIP: {reason})\n")


class ColoredTextTestRunner(unittest.TextTestRunner):
    """Test runner with colored output."""
    
    resultclass = ColoredTextTestResult


def create_test_suite(test_categories=None):
    """
    Create a test suite with specified categories.
    
    Args:
        test_categories: List of test categories to include. If None, includes all.
                        Options: 'basic', 'examples', 'components', 'integration', 'performance'
    """
    suite = unittest.TestSuite()
    
    # Define test categories
    categories = {
        'basic': [TestBasicFunctionality, TestDataStructures],
        'examples': [TestExamples, TestAnalysisScripts],
        'components': [TestModelComponents, TestParameterStructure, TestErrorHandling],
        'integration': [TestIntegrationWorkflows, TestCommandLineInterface, 
                       TestDataAnalysisWorkflow, TestErrorRecovery],
        'performance': [TestPerformance, TestScalability, TestStressTest],
    }
    
    # If no categories specified, include all
    if test_categories is None:
        test_categories = list(categories.keys())
    
    # Add tests from specified categories
    for category in test_categories:
        if category in categories:
            for test_class in categories[category]:
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                suite.addTests(tests)
    
    return suite


def run_test_category(category_name, test_classes, verbosity=2):
    """Run tests for a specific category."""
    print(f"\n{'='*60}")
    print(f"Running {category_name.upper()} Tests")
    print(f"{'='*60}")
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = ColoredTextTestRunner(verbosity=verbosity, stream=sys.stdout)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary for this category
    print(f"\n{category_name.upper()} Tests Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.success_count}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    print(f"  Time: {end_time - start_time:.2f}s")
    
    return result


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run CliMaPan-Lab tests')
    parser.add_argument('--category', choices=['basic', 'examples', 'components', 'integration', 'performance', 'all'],
                       default='all', help='Test category to run')
    parser.add_argument('--verbosity', '-v', type=int, choices=[0, 1, 2], default=2,
                       help='Test output verbosity')
    parser.add_argument('--fast', action='store_true',
                       help='Run only fast tests (excludes performance and stress tests)')
    parser.add_argument('--list', action='store_true',
                       help='List available test categories and exit')
    
    args = parser.parse_args()
    
    # List categories if requested
    if args.list:
        print("Available test categories:")
        print("  basic      - Basic functionality and data structure tests")
        print("  examples   - Example scripts and analysis tools tests")
        print("  components - Model components and parameter tests")
        print("  integration- Integration and workflow tests")
        print("  performance- Performance and scalability tests")
        print("  all        - All test categories")
        return 0
    
    print("CliMaPan-Lab Test Suite")
    print("=" * 60)
    
    # Define test categories
    categories = {
        'basic': [TestBasicFunctionality, TestDataStructures],
        'examples': [TestExamples, TestAnalysisScripts],
        'components': [TestModelComponents, TestParameterStructure, TestErrorHandling],
        'integration': [TestIntegrationWorkflows, TestCommandLineInterface, 
                       TestDataAnalysisWorkflow, TestErrorRecovery],
        'performance': [TestPerformance, TestScalability, TestStressTest],
    }
    
    # Determine which categories to run
    if args.category == 'all':
        if args.fast:
            # Exclude performance tests for fast run
            categories_to_run = ['basic', 'examples', 'components', 'integration']
        else:
            categories_to_run = list(categories.keys())
    else:
        categories_to_run = [args.category]
    
    # Run tests by category
    total_results = {
        'tests_run': 0,
        'successes': 0,
        'failures': 0,
        'errors': 0,
        'skipped': 0,
        'time': 0
    }
    
    overall_start_time = time.time()
    
    for category in categories_to_run:
        if category in categories:
            result = run_test_category(category, categories[category], args.verbosity)
            
            # Accumulate results
            total_results['tests_run'] += result.testsRun
            total_results['successes'] += result.success_count
            total_results['failures'] += len(result.failures)
            total_results['errors'] += len(result.errors)
            total_results['skipped'] += len(result.skipped)
    
    overall_end_time = time.time()
    total_results['time'] = overall_end_time - overall_start_time
    
    # Print overall summary
    print(f"\n{'='*60}")
    print("OVERALL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Categories run: {', '.join(categories_to_run)}")
    print(f"Total tests run: {total_results['tests_run']}")
    print(f"Successes: \033[92m{total_results['successes']}\033[0m")
    print(f"Failures: \033[91m{total_results['failures']}\033[0m")
    print(f"Errors: \033[91m{total_results['errors']}\033[0m")
    print(f"Skipped: \033[93m{total_results['skipped']}\033[0m")
    print(f"Total time: {total_results['time']:.2f}s")
    
    # Calculate success rate
    if total_results['tests_run'] > 0:
        success_rate = (total_results['successes'] / total_results['tests_run']) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    # Return appropriate exit code
    if total_results['failures'] > 0 or total_results['errors'] > 0:
        print(f"\n\033[91mSome tests failed!\033[0m")
        return 1
    elif total_results['tests_run'] == 0:
        print(f"\n\033[93mNo tests were run!\033[0m")
        return 1
    else:
        print(f"\n\033[92mAll tests passed!\033[0m")
        return 0


if __name__ == '__main__':
    sys.exit(main()) 