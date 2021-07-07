import easysnmp
from . import exceptions


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

    def get(self, oids):
        try:
            return super().get(oids)
        except easysnmp.exceptions.EasySNMPConnectionError as e:
            raise exceptions.SNMPConnectionError(e, self, oids)
        except easysnmp.exceptions.EasySNMPNoSuchInstanceError as e:
            raise exceptions.SNMPNoData(e, self, oids)
        except SystemError as e:
            raise exceptions.SNMPError(e, self, oids)

