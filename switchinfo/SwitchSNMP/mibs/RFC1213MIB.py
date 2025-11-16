from .SNMPMib import SNMPMib


# noinspection PyPep8Naming
class RFC1213MIB(SNMPMib):
    def ipNetToMediaTable(self, field_filter: list = None):
        return self.snmp.snmp_table('.1.3.6.1.2.1.4.22.1', {
            1: 'ipNetToMediaIfIndex',
            2: 'ipNetToMediaPhysAddress',
            3: 'ipNetToMediaNetAddress',
            4: 'ipNetToMediaType',
        }, field_filter)
