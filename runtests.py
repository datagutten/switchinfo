#!/usr/bin/env python3
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    if 'USE_NETSNMP' not in os.environ or os.environ['USE_NETSNMP'] == 'True':
        settings.USE_NETSNMP = True
    else:
        settings.USE_NETSNMP = False

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests.tests_cisco_snmp",
                                      "tests.tests_utils", "tests.test_web",
                                      "tests.test_load_info"])
    sys.exit(bool(failures))
