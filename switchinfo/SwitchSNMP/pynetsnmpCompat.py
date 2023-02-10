import pynetsnmp
from pynetsnmp import netsnmp


class PynetsnmpCompat(pynetsnmp.netsnmp.Session):
    def __init__(self, hostname, community, version=2, timeout=0.5, retries=1):
        super().__init__(version=version,
                         timeout=timeout,
                         retries=int(retries - 1),
                         peername=hostname,
                         community=community,
                         community_len=len(community))
        self.open()
