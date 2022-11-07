import re

from . import SwitchSNMP, mibs


class Fortinet(SwitchSNMP):
    def vlans(self):
        mib = mibs.qBridgeMIB(self)
        return mib.dot1qVlanIndex().values()

    def aggregations(self):
        oid = '.1.3.6.1.4.1.12356.106.3.1.0'  # fsTrunkMember.0
        session = self.get_session()
        data = session.get(oid)
        aggregations = {}
        for match in re.findall(r'(.+?):\s(.+?)\s::', data.value):
            aggregations[match[0]] = match[1].split('  ')

        return aggregations
