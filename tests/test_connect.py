from django.test import TestCase

from switchinfo.SwitchSNMP.SNMPError import SNMPError
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class LoadInfoTestCase(TestCase):
    def testInvalidDevice(self):
        snmp = SwitchSNMP('invalid', '127.0.0.1')
        with self.assertRaises(SNMPError) as context:
            snmp.switch_info()
        self.assertContains(str(context.exception), 'Unable to connect to 127.0.0.1 with community invalid:')
