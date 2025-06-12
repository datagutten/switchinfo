from .SNMPMib import SNMPMib


class ifMIB(SNMPMib):
    def ifXTable(self, field_filter=None) -> dict:
        """
        IF-MIB::ifXTable
        :return:
        """
        return self.snmp.snmp_table('.1.3.6.1.2.1.31.1.1.1', {
            1: 'ifName',
            2: 'ifInMulticastPkts',
            3: 'ifInBroadcastPkts',
            4: 'ifOutMulticastPkts',
            5: 'ifOutBroadcastPkts',
            6: 'ifHCInOctets',
            7: 'ifHCInUcastPkts',
            8: 'ifHCInMulticastPkts',
            9: 'ifHCInBroadcastPkts',
            10: 'ifHCOutOctets',
            11: 'ifHCOutUcastPkts',
            12: 'ifHCOutMulticastPkts',
            13: 'ifHCOutBroadcastPkts',
            14: 'ifLinkUpDownTrapEnable',
            15: 'ifHighSpeed',
            16: 'ifPromiscuousMode',
            17: 'ifConnectorPresent',
            18: 'ifAlias',
            19: 'ifCounterDiscontinuityTime',
        }, field_filter)

    def ifTable(self, field_filter=None):
        return self.snmp.snmp_table('.1.3.6.1.2.1.2.2.1', {
            1: 'ifIndex',
            2: 'ifDescr',
            3: 'ifType',
            4: 'ifMtu',
            5: 'ifSpeed',
            6: 'ifPhysAddress',
            7: 'ifAdminStatus',
            8: 'ifOperStatus',
            9: 'ifLastChange',
            10: 'ifInOctets',
            11: 'ifInUcastPkts',
            12: 'ifInNUcastPkts',
            13: 'ifInDiscards',
            14: 'ifInErrors',
            15: 'ifInUnknownProtos',
            16: 'ifOutOctets',
            17: 'ifOutUcastPkts',
            18: 'ifOutNUcastPkts',
            19: 'ifOutDiscards',
            20: 'ifOutErrors',
            21: 'ifOutQLen',
            22: 'ifSpecific',
        }, field_filter)
