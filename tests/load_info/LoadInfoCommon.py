from abc import ABC

from django.test import TestCase

from switchinfo.load_info import switch_info
from tests_unittest.SwitchSNMP.snmp_data import get_file


class LoadInfoCommon(TestCase, ABC):
    @staticmethod
    def get_switch(switch):
        file, ip = get_file(switch)
        return switch_info.switch_info(ip=ip, community=file)

    def setUp(self):
        self.switch_cisco = self.get_switch('cisco')
        self.switch_aruba = self.get_switch('aruba_test')
        self.switch_extreme = self.get_switch('extreme')
