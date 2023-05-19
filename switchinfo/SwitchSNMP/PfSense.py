from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class PfSense(SwitchSNMP):
    arp_mib = 'ipNetToMediaPhysAddress'
