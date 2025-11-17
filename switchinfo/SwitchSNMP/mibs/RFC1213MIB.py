from .SNMPMib import SNMPMib
from .. import utils


# noinspection PyPep8Naming
class RFC1213MIB(SNMPMib):
    def ipNetToMediaTable(self, field_filter: list = None):
        session = self.snmp.get_session()
        oid = '.1.3.6.1.2.1.4.22.1'
        key_mappings = {
            1: 'ipNetToMediaIfIndex',
            2: 'ipNetToMediaPhysAddress',
            3: 'ipNetToMediaNetAddress',
            4: 'ipNetToMediaType',
        }
        data = {}

        for item in session.bulkwalk(oid):
            row, col = utils.table_index(oid, item.oid)

            try:
                field_name = key_mappings[col]
            except KeyError:
                field_name = col

            if row not in data.keys():
                data[row] = {}
            if field_name == 'ipNetToMediaPhysAddress':
                data[row][field_name] = item.hex_string()
            else:
                data[row][field_name] = item.typed_value()

        return data
