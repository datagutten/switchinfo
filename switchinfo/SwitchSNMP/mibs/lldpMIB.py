from .SNMPMib import SNMPMib


# noinspection PyPep8Naming
class lldpMIB(SNMPMib):
    def lldpLocPortTable(self):
        return self.snmp.snmp_table('.1.0.8802.1.1.2.1.3.7.1', {
            1: 'lldpLocPortNum',
            2: 'lldpLocPortIdSubtype',
            3: 'lldpLocPortId',
            4: 'lldpLocPortDesc',
        })

    def lldpRemTable(self):
        return self.snmp.build_dict_multikeys('.1.0.8802.1.1.2.1.4.1.1',
                                              ['lldpRemTimeMark', 'lldpRemLocalPortNum', 'lldpRemIndex'],
                                              {1: 'lldpRemTimeMark',
                                               2: 'lldpRemLocalPortNum',
                                               3: 'lldpRemIndex',
                                               4: 'lldpRemChassisIdSubtype',
                                               5: 'lldpRemChassisId',
                                               6: 'lldpRemPortIdSubtype',
                                               7: 'lldpRemPortId',
                                               8: 'lldpRemPortDesc',
                                               9: 'lldpRemSysName',
                                               10: 'lldpRemSysDesc',
                                               11: 'lldpRemSysCapSupported',
                                               12: 'lldpRemSysCapEnabled'
                                               },
                                              key='lldpRemLocalPortNum')

    def lldpRemManAddrTable(self):
        return self.snmp.build_dict_multikeys('.1.0.8802.1.1.2.1.4.2.1',
                                              ['lldpRemTimeMark', 'lldpRemLocalPortNum',
                                               'lldpRemIndex', 'lldpRemManAddrSubtype',
                                               'lldpRemManAddr'],
                                              {
                                                  1: 'lldpRemManAddrSubtype',
                                                  2: 'lldpRemManAddr',
                                                  3: 'lldpRemManAddrIfSubtype',
                                                  4: 'lldpRemManAddrIfId',
                                                  5: 'lldpRemManAddrOID',
                                              },
                                              key='lldpRemLocalPortNum')
