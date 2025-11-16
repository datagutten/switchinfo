from .SNMPMib import SNMPMib


# noinspection PyPep8Naming
class qBridgeMIB(SNMPMib):
    def dot1qVlanIndex(self):
        """
        dot1qVlanIndex
        :return:
        """
        return self.snmp.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.2.1.2', int_index=True)
