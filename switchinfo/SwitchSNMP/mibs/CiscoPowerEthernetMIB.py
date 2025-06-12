from .SNMPMib import SNMPMib


# noinspection PyPep8Naming
class CiscoPowerEthernetMIB(SNMPMib):
    def cpeExtPsePortTable(self, field_filter: list = None):
        fields = {
            1: "cpeExtPsePortEnable",
            2: "cpeExtPsePortDiscoverMode",
            3: "cpeExtPsePortDeviceDetected",
            4: "cpeExtPsePortIeeePd",
            5: "cpeExtPsePortAdditionalStatus",
            6: "cpeExtPsePortPwrMax",
            7: "cpeExtPsePortPwrAllocated",
            8: "cpeExtPsePortPwrAvailable",
            9: "cpeExtPsePortPwrConsumption",
            10: "cpeExtPsePortMaxPwrDrawn",
            11: "cpeExtPsePortEntPhyIndex",
            12: "cpeExtPsePortPolicingCapable",
            13: "cpeExtPsePortPolicingEnable",
            14: "cpeExtPsePortPolicingAction",
            15: "cpeExtPsePortPwrManAlloc",
            16: "cpeExtPsePortCapabilities"
        }
        return self.snmp.snmp_table('.1.3.6.1.4.1.9.9.402.1.2.1', fields, field_filter)
