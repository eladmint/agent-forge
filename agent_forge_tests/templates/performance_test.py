#!/usr/bin/env python3
"""
Performance Test Template
========================

Template for creating performance tests.
"""

from .basic_test import BasicAgentTest


class PerformanceTest(BasicAgentTest):
    """Template for performance tests."""
    
    def test_basic_performance(self):
        """Test basic performance metrics."""
        # Override this method with your performance tests
        pass


if __name__ == '__main__':
    import unittest
    unittest.main()