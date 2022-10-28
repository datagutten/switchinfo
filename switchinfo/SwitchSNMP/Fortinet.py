from . import SwitchSNMP, mibs


class Fortinet(SwitchSNMP):
    def vlans(self):
        mib = mibs.qBridgeMIB(self)
        return mib.dot1qVlanIndex().values()
