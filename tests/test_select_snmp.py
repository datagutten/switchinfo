from django.conf import settings

from switchinfo.SwitchSNMP.EasySNMPCompat import EasySNMPCompat
from switchinfo.SwitchSNMP.NetSNMPCompat import NetSNMPCompat
from switchinfo.SwitchSNMP import select
from django.test import TestCase
from switchinfo import models


class LoadInfoTestCase(TestCase):
    def test_library_fallback(self):
        del settings.SNMP_LIBRARY
        snmp = select.get_switch(models.Switch(ip='127.0.0.1'))
        self.assertIsInstance(snmp.get_session(), EasySNMPCompat)

    def test_use_easysnmp(self):
        del settings.SNMP_LIBRARY
        settings.USE_EASYSNMP = True
        snmp = select.get_switch(models.Switch(ip='127.0.0.2'))
        self.assertIsInstance(snmp.get_session(), EasySNMPCompat)

    def test_use_netsnmp(self):
        del settings.SNMP_LIBRARY
        settings.USE_NETSNMP = True
        snmp = select.get_switch(models.Switch(ip='127.0.0.3'))
        self.assertIsInstance(snmp.get_session(), NetSNMPCompat)

    def test_easysnmp(self):
        settings.SNMP_LIBRARY = 'easysnmp'
        snmp = select.get_switch(models.Switch(ip='127.0.0.4'))
        self.assertIsInstance(snmp.get_session(), EasySNMPCompat)

    def test_netsnmp(self):
        settings.SNMP_LIBRARY = 'netsnmp'
        snmp = select.get_switch(models.Switch(ip='127.0.0.5'))
        self.assertIsInstance(snmp.get_session(), NetSNMPCompat)
