def get_switch(switch):
        if switch.type=='Cisco':
            from switchinfo.SwitchSNMP.Cisco import Cisco as snmp
        elif switch.type=='Extreme':
            from switchinfo.SwitchSNMP.Extreme import Extreme as snmp
        else:
            from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP as snmp
        if snmp:
            return snmp(community=switch.community, device=switch.ip)
        else:
            return False