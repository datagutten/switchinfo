class SNMPError(ValueError):
    session = None

    def __init__(self, e, session):
        self.session = session
        self.e = e

    def __str__(self):
        return 'Unable to connect to %s with community %s: %s' % (self.session.hostname, self.session.community, self.e)


class SNMPNoData(ValueError):
    oid = None

    def __init__(self, oid):
        self.oid = oid

    def __str__(self):
        return 'No data for oid %s' % self.oid
