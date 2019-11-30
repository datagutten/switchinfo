from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class ArubaVSF(SwitchSNMP):
    def stack_ports(self):
        oid = '.1.3.6.1.4.1.11.2.14.11.5.1.116.1.5.1.2'
        return self.create_dict(oid=oid, int_index=True)
