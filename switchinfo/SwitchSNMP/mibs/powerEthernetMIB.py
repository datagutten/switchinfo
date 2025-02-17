from .SNMPMib import SNMPMib


# noinspection PyPep8Naming
class powerEthernetMIB(SNMPMib):
    states = {
        0: 'disabled',  # Extreme use 0 for disabled
        1: 'disabled',
        2: 'searching',
        3: 'deliveringPower',
        4: 'fault',
        5: 'test',
        6: 'otherFault'
    }

    def pethPsePortTable(self):
        return self.snmp.build_dict_multikeys(
            '.1.3.6.1.2.1.105.1.1.1',
            ['pethPsePortGroupIndex', 'pethPsePortIndex'],
            {
                1: 'pethPsePortGroupIndex',
                2: 'pethPsePortIndex',
                3: 'pethPsePortAdminEnable',
                4: 'pethPsePortPowerPairsControlAbility',
                5: 'pethPsePortPowerPairs',
                6: 'pethPsePortDetectionStatus',
                7: 'pethPsePortPowerPriority',
                8: 'pethPsePortMPSAbsentCounter',
                9: 'pethPsePortType',
                10: 'pethPsePortPowerClassifications',
                11: 'pethPsePortInvalidSignatureCounter',
                12: 'pethPsePortPowerDeniedCounter',
                13: 'pethPsePortOverLoadCounter',
                14: 'pethPsePortShortCounter',
            })
