import easysnmp
from switchinfo.SwitchSNMP import SNMPError


class EasySNMPCompat(easysnmp.Session):
    def __init__(self, hostname, community, version=2, timeout=0.5, retries=1):
        try:
            super().__init__(hostname=hostname, community=community,
                             version=version, timeout=timeout, retries=retries,
                             abort_on_nonexistent=True)
        except easysnmp.exceptions.EasySNMPConnectionError as e:
            raise SNMPError.SNMPError(e, self)
        except SystemError as e:
            raise SNMPError.SNMPError(e, self)

    def get(self, oids):
        try:
            return super().get(oids)
        except easysnmp.exceptions.EasySNMPConnectionError as e:
            raise SNMPError.SNMPError(e, self)
        except easysnmp.exceptions.EasySNMPNoSuchInstanceError:
            raise SNMPError.SNMPNoData(oids)
        except SystemError as e:
            raise SNMPError.SNMPError(e, self)

