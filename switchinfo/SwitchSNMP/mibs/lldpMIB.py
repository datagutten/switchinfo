import warnings

from snmp_compat import SNMPResponse

from .SNMPMib import SNMPMib
from .. import utils


# noinspection PyPep8Naming
class lldpMIB(SNMPMib):
    def lldpLocPortTable(self):
        return self.snmp.snmp_table('.1.0.8802.1.1.2.1.3.7.1', {
            1: 'lldpLocPortNum',
            2: 'lldpLocPortIdSubtype',
            3: 'lldpLocPortId',
            4: 'lldpLocPortDesc',
        })

    def lldpRemTable(self) -> dict[int, dict]:
        data = self.snmp.build_dict_multikeys('.1.0.8802.1.1.2.1.4.1.1',
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
                                              key='lldpRemLocalPortNum', value_obj=True)
        for port, neighbor in data.items():
            if neighbor['lldpRemPortIdSubtype'].typed_value() == 3:  # macAddress
                neighbor['lldpRemPortId'] = neighbor['lldpRemPortId'].hex_string()
            elif neighbor['lldpRemPortIdSubtype'].typed_value() == 4:  # networkAddress
                neighbor['lldpRemPortId'] = neighbor['lldpRemPortId'].ip_address()
            else:
                neighbor['lldpRemPortId'] = neighbor['lldpRemPortId'].typed_value()

            if neighbor['lldpRemChassisIdSubtype'] == 4:  # macAddress
                neighbor['lldpRemChassisIdSubtype'] = neighbor['lldpRemChassisId'].hex_string()

            neighbor.update({key: value.typed_value() for key, value in neighbor.items() if
                             issubclass(type(value), SNMPResponse)})
        return data

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

    @staticmethod
    def remote_helper(remote: dict) -> dict:
        """
        Get values from an entry from lldpRemTable
        :param remote: Entry from lldpRemTable
        :return: Parsed data
        """
        neighbor = {
            'device_id': remote['lldpRemSysName'],
            'platform': remote['lldpRemSysDesc'],
            'local_port_num': remote['lldpRemLocalPortNum'],
        }

        if remote['lldpRemPortIdSubtype'] == 3 and len(remote['lldpRemPortId']) != 12:  # macAddress
            warnings.warn('Invalid MAC-address "%s"' % remote['lldpRemPortId'])
        neighbor['remote_port'] = remote['lldpRemPortId']
        if remote['lldpRemChassisIdSubtype'] == 4:  # macAddress
            neighbor['mac'] = remote['lldpRemChassisId']

        return neighbor

    @staticmethod
    def remote_address_helper(address: dict):
        """
        Get values from an entry from lldpRemManAddrTable
        :param address: Entry from lldpRemManAddrTable
        :return: Parsed MAC address and IP
        """
        neighbor = {}
        if address['lldpRemManAddrSubtype'] == 6:  # all802
            neighbor['mac'] = utils.mac_parse_oid(address['lldpRemManAddr'])
        elif address['lldpRemManAddrSubtype'] == 1 and utils.validate_ip(address['lldpRemManAddr']):  # ipV4
            neighbor['ip'] = address['lldpRemManAddr']
        else:
            print('Unknown address type %d' % address['lldpRemManAddrSubtype'], address['lldpRemManAddr'])
            neighbor['unknown'] = address['lldpRemManAddr']
        return neighbor
