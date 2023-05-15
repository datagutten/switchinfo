import easysnmp
from easysnmp import SNMPVariable as EasySNMPVariable

from . import exceptions, SNMPVariable as CustomSNMPVariable


class EasySNMPCompat(easysnmp.Session):
    def __init__(self, hostname, community, version=2, timeout=0.5, retries=1):
        try:
            super().__init__(hostname=hostname, community=community,
                             version=version, timeout=timeout, retries=retries,
                             abort_on_nonexistent=True)
        except easysnmp.exceptions.EasySNMPConnectionError as e:
            raise exceptions.SNMPConnectionError(e, self)
        except SystemError as e:
            raise exceptions.SNMPError(e, self)

    def close(self):
        pass

    def get(self, oids):
        try:
            return convert_variable(super().get(oids))
        except easysnmp.exceptions.EasySNMPTimeoutError as e:
            raise exceptions.SNMPTimeout(e, self, oids)
        except easysnmp.exceptions.EasySNMPConnectionError as e:
            raise exceptions.SNMPConnectionError(e, self, oids)
        except easysnmp.exceptions.EasySNMPNoSuchInstanceError as e:
            raise exceptions.SNMPNoData(e, self, oids)
        except SystemError as e:
            raise exceptions.SNMPError(e, self, oids)

    def walk(self, oids='.1.3.6.1.2.1'):
        try:
            return list(map(lambda var: convert_variable(var), super().walk(oids)))
        except easysnmp.exceptions.EasySNMPTimeoutError as e:
            raise exceptions.SNMPTimeout(e, self, oids)
        except easysnmp.exceptions.EasySNMPConnectionError as e:
            raise exceptions.SNMPConnectionError(e, self, oids)
        except easysnmp.exceptions.EasySNMPNoSuchInstanceError as e:
            raise exceptions.SNMPNoData(e, self, oids)
        except SystemError as e:
            raise exceptions.SNMPError(e, self, oids)


def convert_variable(var: EasySNMPVariable):
    return CustomSNMPVariable(oid=var.oid, oid_index=var.oid_index, value=var.value, snmp_type=var.snmp_type)
