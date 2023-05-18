from abc import ABC

from django.test import TestCase

from switchinfo.load_info import switch_info
from tests_unittest.SwitchSNMP.snmp_data import get_file


class LoadInfoCommon(TestCase, ABC):
    def setUp(self):
        file, ip = get_file('cisco')
        self.switch_cisco = switch_info.switch_info(ip=ip, community=file)
        file, ip = get_file('aruba_test')
        self.switch_aruba = switch_info.switch_info(ip=ip, community=file)
        file, ip = get_file('extreme')
        self.switch_extreme = switch_info.switch_info(ip=ip, community=file)
