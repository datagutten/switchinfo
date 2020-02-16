class SNMPError(ValueError):
    session = None

    def __init__(self, e, session):
        self.session = session
        self.e = e

    def __str__(self):
        return 'Unable to connect to %s with community %s: %s' % (self.session.hostname, self.session.community, self.e)
