import datetime
import re


def parse_port_list(string: bytes, limit=None, zero_count=False):
    """
    Parse a binary port list
    :param string:
    :param limit:
    :param zero_count: Count index from zero
    :return:
    """
    ports = dict()
    for pos, byte in enumerate(string):
        binary = format(byte, '08b')
        offset = 8 * pos
        for binpos, binbyte in enumerate(binary):
            if not zero_count:
                index = binpos + offset + 1
            else:
                index = binpos + offset
            # print('Port: %d Byte: %s' % (index, binbyte))
            if binbyte == '1':
                ports[index] = True
            else:
                ports[index] = False
            if limit and index >= limit:
                return ports
    return ports


def table_index(base_oid, oid):
    """
    Get the row and col from an SNMP table entry oid
    """
    if oid.find('iso') == 0:
        oid = oid.replace('iso', '.1')

    oid_key = oid[len(base_oid):]
    matches = re.search(r'^\.(\d+)\.([\d.]+)', oid_key)
    col = int(matches.group(1))
    try:
        row = int(matches.group(2))
    except ValueError:
        row = matches.group(2)
    return row, col


def last_section(oid):
    match = re.match(r'.+\.([0-9]+)', oid)
    if match:
        return match.group(1)


def mac_parse_oid(oid):
    octets = oid.split('.')
    string = ''
    for octet in octets:
        octet = int(octet)
        if octet <= 0x0f:
            string += '0'
        string += format(octet, 'x')
    return string


def validate_ip(ip: str):
    if re.match(r'^(?:\b\.?(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){4}$', ip):
        return True
    else:
        return False




def translate_status(status: str) -> int:
    try:
        return int(status)
    except ValueError:
        status_names = {
            'up': 1,
            'down': 2,
            'testing': 3,
            'unknown': 4,
            'dormant': 5,
            'notPresent': 6,
            'lowerLayerDown': 7,
        }

        if status not in status_names:
            return 5
        else:
            return status_names[status]
