from .SNMPMib import SNMPMib


# noinspection PyPep8Naming
class entityMIB(SNMPMib):
    def entPhysicalTable(self):
        fields = {
            1: "entPhysicalIndex",
            2: "entPhysicalDescr",
            3: "entPhysicalVendorType",
            4: "entPhysicalContainedIn",
            5: "entPhysicalClass",
            6: "entPhysicalParentRelPos",
            7: "entPhysicalName",
            8: "entPhysicalHardwareRev",
            9: "entPhysicalFirmwareRev",
            10: "entPhysicalSoftwareRev",
            11: "entPhysicalSerialNum",
            12: "entPhysicalMfgName",
            13: "entPhysicalModelName",
            14: "entPhysicalAlias",
            15: "entPhysicalAssetID",
            16: "entPhysicalIsFRU",
            17: "entPhysicalMfgDate",
            18: "entPhysicalUris",
        }
        return self.snmp.build_dict_multikeys('.1.3.6.1.2.1.47.1.1.1.1', ['entPhysicalIndex'], fields)
