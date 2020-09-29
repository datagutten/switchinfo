from django.test import TestCase

from switchinfo.SwitchSNMP.exceptions import SNMPError
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class LoadInfoTestCase(TestCase):
    def testInvalidDevice(self):
        self.skipTest('Not working')
        snmp = SwitchSNMP('invalid', '127.0.0.1')
        with self.assertRaises(SNMPError) as context:
            snmp.switch_info()
        self.assertIn('Unable to connect to 127.0.0.1 with community invalid:',
                      str(context.exception))
