from datetime import timedelta

# noinspection PyProtectedMember,PyUnresolvedReferences
from netsnmp._api import SNMPError as EasySNMPError

import netsnmp
from easysnmp import SNMPVariable
from easysnmp.exceptions import EasySNMPNoSuchNameError
from . import exceptions


class NetSNMPCompat(netsnmp.SNMPSession):
    session = None
    hostname = None

    def __init__(self, hostname, community, version=0, timeout=0.5, retries=1):
        self.hostname = hostname
        super().__init__(peername=hostname, community=community, version=version, timeout=timeout, retries=retries)

    def get(self, oids):
        if isinstance(oids, list):
            is_list = True
        else:
            is_list = False
        try:
            data = super().get(oids)
        except EasySNMPNoSuchNameError as e:
            raise exceptions.SNMPNoData(e)
        except EasySNMPError as e:
            print(e)
            if str(e).find('null response') > -1:
                raise exceptions.SNMPNoData(e)
            raise exceptions.SNMPError(e, self)

        return convert_response(data, is_list)

    def walk(self, oids):
        elements = []
        try:
            data = super().walk(oids)
            for element in data:
                elements.append(convert_response(element))
            return elements
        except EasySNMPError as e:
            if str(e).find('null response') > -1:
                raise exceptions.SNMPNoData(e)
            else:
                raise exceptions.SNMPError(e, self)


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
        elif response[1] == 'NULL':
            raise exceptions.SNMPNoData(response[0])
        else:
            value = response[2]

        variable = SNMPVariable(oid=response[0], snmp_type=response[1], value=value)
        variable.oid = 'iso' + response[0][2:]
        return variable


class Response:
    value = None

    def __init__(self, value):
        self.value = value
