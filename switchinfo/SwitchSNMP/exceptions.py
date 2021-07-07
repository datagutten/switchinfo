class SNMPError(ValueError):
    session = None
    oid: str = None

    def __init__(self, e: Exception = None, session=None, oid: str = None):
        self.session = session
        self.e = e
        self.oid = oid


class SNMPConnectionError(SNMPError):
    def __str__(self):
        return 'Unable to connect to %s with community %s: %s' % (
            self.session.hostname, self.session.community, self.e)


class SNMPNoData(SNMPError):
    def __str__(self):
        return 'No data for oid %s' % self.oid


class SNMPTimeout(SNMPError):
    def __str__(self):
        return 'Timeout for oid %s' % self.oid
