#!/usr/bin/env python3
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    if len(sys.argv) == 1:
        tests = ["tests.tests_utils", "tests.test_web"]
    else:
        tests = sys.argv[1:]

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(tests)
    sys.exit(bool(failures))
