import os
import unittest
# python3 -m tests.test_snmp
from switchinfo.SwitchSNMP import exceptions

if 'USE_NETSNMP' not in os.environ or os.environ['USE_NETSNMP'] == 'true':
    use_netsnmp = True
else:
    use_netsnmp = False

if use_netsnmp:
    from switchinfo.SwitchSNMP.NetSNMPCompat import NetSNMPCompat \
        as SNMPSession
else:
    from switchinfo.SwitchSNMP.EasySNMPCompat import EasySNMPCompat \
        as SNMPSession


class SNMPTestCase(unittest.TestCase):
    session = None

    def test_empty_value(self):
        session = SNMPSession('127.0.0.1', 'cisco')
        with self.assertRaises(exceptions.SNMPNoData) as context:
            session.get('.1.3.6.1.2.1.1.6')
        self.assertEqual('No data for oid .1.3.6.1.2.1.1.6',
                         str(context.exception))

    def test_invalid_oid(self):
        session = SNMPSession('127.0.0.1', 'cisco')
        with self.assertRaises(exceptions.SNMPNoData) as context:
            session.get('.1.7.7.7.7')
        self.assertEqual('No data for oid .1.7.7.7.7',
                         str(context.exception))

    def test_connection_error(self):
        session = SNMPSession('127.0.0.1', 'ciscobad')
        with self.assertRaises(exceptions.SNMPConnectionError) as context:
            session.get('.1.3.6.1.2.1.1.6')
        self.assertIn('Unable to connect to 127.0.0.1 with community ciscobad',
                      str(context.exception))

    def test_timeout(self):
        session = SNMPSession('127.0.0.1', 'ciscobad')
        with self.assertRaises(exceptions.SNMPTimeout) as context:
            session.get('.1.3.6.1.2.1.1.6')
        self.assertIn(
            'Timeout for oid .1.3.6.1.2.1.1.6',
            str(context.exception))

    def test_empty_string(self):
        session = SNMPSession('127.0.0.1', 'cisco')
        response = session.get('.1.3.6.1.2.1.31.1.1.1.18.1')
        self.assertEqual('', response.value)


if __name__ == "__main__":
    unittest.main()  # run all tests
