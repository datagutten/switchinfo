from switchinfo.SwitchSNMP.Cisco import Cisco
from switchinfo.SwitchSNMP.Extreme import Extreme
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.SwitchSNMP.ArubaVSF import ArubaVSF
from switchinfo.SwitchSNMP.ArubaCX import ArubaCX


def get_switch(switch):
    if switch.type == 'Cisco':
        snmp = Cisco
    elif switch.type == 'Extreme':
        snmp = Extreme
    elif switch.type == 'Aruba':
        snmp = ArubaVSF
    elif switch.type == 'Aruba CX':
        snmp = ArubaCX
    else:
        snmp = SwitchSNMP

    return snmp(community=switch.community, device=switch.ip)
