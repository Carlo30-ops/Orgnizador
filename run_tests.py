#!/usr/bin/env python
"""Ejecuta todos los tests del proyecto."""
import sys
import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    start_dir = "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
