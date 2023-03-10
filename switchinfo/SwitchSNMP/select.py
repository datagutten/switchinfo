from switchinfo.SwitchSNMP.Cisco import Cisco
from switchinfo.SwitchSNMP.Extreme import Extreme
from switchinfo.SwitchSNMP.Fortinet import Fortinet
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.SwitchSNMP.ArubaVSF import ArubaVSF
from switchinfo.SwitchSNMP.ArubaCX import ArubaCX
from switchinfo import SwitchSNMP as SwitchSNMPModule


def get_switch(switch):
    if switch.type == 'Cisco':
        snmp = Cisco
    elif switch.type == 'Extreme':
        snmp = Extreme
    elif switch.type == 'Fortinet':
        snmp = Fortinet
    elif switch.type == 'Aruba':
        snmp = ArubaVSF
    elif switch.type == 'Aruba CX':
        snmp = ArubaCX
    elif switch.type == 'Westermo':
        snmp = SwitchSNMPModule.Westermo
    else:
        snmp = SwitchSNMP

    return snmp(community=switch.community, device=switch.ip)
