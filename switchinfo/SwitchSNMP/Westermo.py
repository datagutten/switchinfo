from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class Westermo(SwitchSNMP):
    lldp_key = 'bridge_port'
    timeout = 5

    interface_types = [
        6,  # ethernetCsmacd
        117,  # gigabitEthernet
        169,  # shdsl
    ]
