from datetime import timedelta

import netsnmp
from easysnmp import SNMPVariable


class NetSNMPCompat(netsnmp.SNMPSession):
    session = None

    def get(self, oids):
        if isinstance(oids, list):
            is_list = True
        else:
            is_list = False
        return convert_response(super().get(oids), is_list)

    def walk(self, oids):
        elements = []
        data = super().walk(oids)

        for element in data:
            elements.append(convert_response(element))
        return elements


def convert_response(response, is_list=False):
    # if response.type ==
    if is_list:
        elements = []
        for element in response:
            elements.append(convert_response(element))
        return elements
    else:
        if isinstance(response, list):
            response = response[0]

        if response[1] == 'STRING':
            value = response[2].replace('"', '')
        elif response[1] == 'Timeticks':
            import re
            matches = re.findall(r'[0-9]+', response[2])
            delta = timedelta(days=int(matches[0]), hours=int(matches[1]), minutes=int(matches[2]), seconds=int(matches[3]), milliseconds=int(matches[4]))
            value = str(int(delta.total_seconds()))
            value += str(int(delta.microseconds/1000))
        elif response[1] == 'Hex-STRING':
            import re
            matches = re.findall(r'([A-F0-9]{2})\s', response[2])
            value = ''
            for byte in matches:
                byte = int(byte, 16)
                value += chr(byte)
        else:
            value = response[2]

        variable = SNMPVariable(oid=response[0], snmp_type=response[1], value=value)
        variable.oid = 'iso' + response[0][2:]
        return variable


class Response:
    value = None

    def __init__(self, value):
        self.value = value
