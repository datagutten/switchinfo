from switchinfo import load_info
from switchinfo.load_info import switch_info
from switchinfo.models import Mac
from tests.load_info.LoadInfoCommon import LoadInfoCommon
from tests_unittest.SwitchSNMP.snmp_data import get_file


class LoadMacTestCase(LoadInfoCommon):
    def testLoadMacCisco(self):
        file, ip = get_file('ROV-SW-04')
        switch = switch_info.switch_info(ip=ip, community=file)
        switch.vlan.create(vlan=12)
        load_info.load_interfaces(switch)
        switch.vlan.exclude(vlan=12).delete()
        load_info.load_mac(switch)

        interface = switch.interfaces.exclude(macs=None).first()
        self.assertGreater(Mac.objects.all().count(), 0)
        self.assertEqual('Gi1/5', interface.interface)
        self.assertEqual('Vanlig patchepunkt Vlan 12', interface.description)
        self.assertEqual('4437e6ecfcf7', interface.macs.first().mac)

    def testLoadMacAruba(self):
        load_info.load_interfaces(self.switch_aruba)
        load_info.load_mac(self.switch_aruba)
        interface = self.switch_aruba.interfaces.exclude(macs=None).first()
        self.assertGreater(Mac.objects.all().count(), 0)
        self.assertEqual('8', interface.interface)
        self.assertEqual('005056a94fa3', interface.macs.first().mac)
