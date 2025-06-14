#!/usr/bin/env python3
"""
Production Readiness Test Suite
===============================

Comprehensive production readiness validation for Agent Forge.
"""

from .quick_start import QuickStartTestSuite


class ProductionReadinessTestSuite(QuickStartTestSuite):
    """Production readiness test suite."""
    
    def run_production_tests(self):
        """Run production readiness tests."""
        return self.run_all_tests(verbose=True)


if __name__ == '__main__':
    suite = ProductionReadinessTestSuite()
    results = suite.run_production_tests()
    print(f"Production readiness: {'READY' if results.all_passed else 'NOT READY'}")