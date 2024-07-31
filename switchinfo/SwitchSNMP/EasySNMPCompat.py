import easysnmp
from easysnmp import SNMPVariable as EasySNMPVariable

from . import exceptions, SNMPVariable as CustomSNMPVariable, utils
from .compat.SNMPCompat import SNMPCompat


class EasySNMPCompat(easysnmp.Session, SNMPCompat):
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
        except easysnmp.exceptions.EasySNMPError as e:
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
    return CustomEasySNMPVariable(oid=var.oid, oid_index=var.oid_index, value=var.value, snmp_type=var.snmp_type)


class CustomEasySNMPVariable(CustomSNMPVariable):
    def typed_value(self):
        if self.snmp_type == 'OCTETSTR':
            try:
                return int(self.value)
            except ValueError:
                return self.value or None
        elif self.snmp_type in ['INTEGER', 'COUNTER', 'COUNTER64', 'GAUGE']:
            return int(self.value)
        elif self.snmp_type == 'TICKS':
            return utils.timeticks(int(self.value))
        elif self.snmp_type == 'OBJECTID':
            return self.value  # Value 'ccitt.0.0'
        else:
            return self.value
