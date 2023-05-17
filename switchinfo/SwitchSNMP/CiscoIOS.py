import re

from switchinfo.SwitchSNMP import Cisco


class CiscoIOS(Cisco):
    """
    Cisco IOS 12 or 15
    """
    poe_absolute_index = False

    @staticmethod
    def module_to_ifindex(module: int, index: int):
        return 10100 + (500 * (module - 1)) + index

    @staticmethod
    def ifindex_to_module(index: int):
        if index < 10000:
            return [None, None]
        module = int(str(index)[1:3])  # First three digits indicates the module
        port = int(str(index)[3:5])  # Last two digits are the port
        quotient, remainder = divmod(module, 6)
        if remainder > 1:
            return [None, None]
        return [quotient + 1, port]

    def interface_poe(self):
        interfaces = super().interface_poe()
        interfaces_converted = {}
        for key, interface in interfaces.items():
            module, index = key.split('.')
            if_index = self.module_to_ifindex(int(module), int(index))
            interfaces_converted[if_index] = interface

        return interfaces_converted

