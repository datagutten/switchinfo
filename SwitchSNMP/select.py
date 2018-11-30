from switchinfo.SwitchSNMP.Cisco import Cisco
from switchinfo.SwitchSNMP.Extreme import Extreme
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


def get_switch(switch):
    if switch.type == 'Cisco':
        snmp = Cisco
    elif switch.type == 'Extreme':
        snmp = Extreme
    else:
        snmp = SwitchSNMP

    return snmp(community=switch.community, device=switch.ip)
