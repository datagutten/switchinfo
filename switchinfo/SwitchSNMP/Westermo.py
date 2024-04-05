from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class Westermo(SwitchSNMP):
    lldp_key = 'bridge_port'
    timeout = 5
