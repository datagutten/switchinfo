from switchinfo.SwitchSNMP import Cisco


class CiscoIOS(Cisco):
    """
    Cisco IOS 12 or 15
    """
    poe_snmp_key = 'entPhysicalAlias'
    poe_db_key = 'index'


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
