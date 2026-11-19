"""Regression checks for both independent C sampler compilation entry points."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

import checker

spec = importlib.util.spec_from_file_location(
    'mapping_checker_flags', Path(__file__).parent/'independent/mapping_checker.py')
mapping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapping)


class SharedLibrarySettings(unittest.TestCase):
    def test_macos(self):
        for module in (checker, mapping):
            with self.subTest(module=module.__name__), patch.object(module.sys, 'platform', 'darwin'):
                self.assertEqual(module.shared_library_settings(), ('.dylib', ['-dynamiclib']))

    def test_linux(self):
        for module in (checker, mapping):
            with self.subTest(module=module.__name__), patch.object(module.sys, 'platform', 'linux'):
                self.assertEqual(module.shared_library_settings(), ('.so', ['-shared', '-fPIC']))

    def test_unsupported_platform(self):
        for module in (checker, mapping):
            with self.subTest(module=module.__name__), patch.object(module.sys, 'platform', 'win32'):
                with self.assertRaises(RuntimeError):
                    module.shared_library_settings()


if __name__ == '__main__':
    unittest.main()
