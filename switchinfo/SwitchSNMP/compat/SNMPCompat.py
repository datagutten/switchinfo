from abc import ABC

from switchinfo.SwitchSNMP import SNMPVariable


class SNMPCompat(ABC):
    def get(self, oid) -> SNMPVariable:
        raise NotImplementedError()

    def walk(self, oid):
        raise NotImplementedError()
