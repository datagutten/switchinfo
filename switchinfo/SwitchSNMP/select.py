from django.conf import settings

from switchinfo.SwitchSNMP.Cisco import Cisco
from switchinfo.SwitchSNMP.Extreme import Extreme
from switchinfo.SwitchSNMP.Fortinet import Fortinet
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.SwitchSNMP.ArubaVSF import ArubaVSF
from switchinfo.SwitchSNMP.ArubaCX import ArubaCX
from switchinfo.SwitchSNMP.ArubaCXREST import ArubaCXREST
from switchinfo import SwitchSNMP as SwitchSNMPModule
from switchinfo import SwitchAPI

from switchinfo.models import Switch


def select_snmp_library():
    if hasattr(settings, 'SNMP_LIBRARY'):
        return settings.SNMP_LIBRARY
    elif hasattr(settings, 'USE_NETSNMP') and settings.USE_NETSNMP is True:
        return 'netsnmp'
    else:
        return 'easysnmp'


def get_login(switch: Switch):
    try:
        from config_backup import ConfigBackup
    except ImportError:
        return None, None

    try:
        options = ConfigBackup.backup_options(switch)
        return options.username, options.password
    except ConfigBackup.BackupFailed:
        return None, None


def get_switch(switch: Switch) -> SwitchSNMP:
    if switch.type == 'Cisco':
        snmp = SwitchSNMPModule.CiscoIOS
    elif switch.type == 'Cisco IOS XE':
        snmp = SwitchSNMPModule.CiscoIOSXE
    elif switch.type == 'Extreme':
        snmp = Extreme
    elif switch.type == 'Fortinet':
        snmp = [SwitchAPI.FortinetAPI, Fortinet]
    elif switch.type == 'Aruba':
        snmp = ArubaVSF
    elif switch.type == 'Aruba CX':
        snmp = [ArubaCXREST, ArubaCX]
    elif switch.type == 'Aruba CX REST API':
        snmp = ArubaCXREST
    elif switch.type == 'Westermo':
        snmp = SwitchSNMPModule.Westermo
    elif switch.type == 'pfSense':
        snmp = SwitchSNMPModule.PfSense
    else:
        snmp = SwitchSNMP

    username, password = get_login(switch)
    if type(snmp) != list:
        snmp = [snmp]
    for snmp_class in snmp:
        try:
            return snmp_class(community=switch.community, device=switch.ip, switch=switch,
                              snmp_library=select_snmp_library(),
                              username=username, password=password)
        except SwitchAPI.api_exceptions.APIError:
            continue  # Login or API initialization failed
        except TypeError:  # SNMP class without username and password arguments
            return snmp_class(community=switch.community, device=switch.ip, switch=switch,
                              snmp_library=select_snmp_library())
