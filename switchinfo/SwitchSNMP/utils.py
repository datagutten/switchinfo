import datetime
import re


def parse_port_list(string, limit=None, zero_count=False):
    """
    Parse a binary port list
    :param string:
    :param limit:
    :param zero_count: Count index from zero
    :return:
    """
    ports = dict()
    for pos, byte in enumerate(string):
        binary = format(ord(byte), '08b')
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


def parse_mac(mac):
    mac_address = []
    for char in mac:
        mac_address.append(ord(char))
    return mac_address


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


def mac_string(mac_address):
    string = ''
    if len(mac_address) == 12:  # No conversion required
        return mac_address

    for octet in mac_address:
        octet = ord(octet)
        if octet <= 0x0f:
            string += '0'
        # Format as lower case hex digit without prefix
        string += format(octet, 'x')
    return string


def timeticks(ticks: int) -> datetime.timedelta:
    return datetime.timedelta(seconds=ticks / 100)


def validate_ip(ip: str):
    if re.match(r'^(?:\b\.?(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){4}$', ip):
        return True
    else:
        return False


def ip_string(ip):
    string = ''
    for section in ip:
        string += '%s.' % ord(section)
    return string[:-1]


def name_string(name):
    string = ''
    for char in name:
        string += '%s.' % ord(char)
    return string


def check_and_set(data, snmp_object, oid, key):
    if snmp_object.oid.find(oid) >= 0 and snmp_object.value:
        data.update({key: snmp_object.value})


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


def parse_interface(interface):
    matches = re.match(r'^(\D+)?(\d)(?:/\d)?/(\d+)', interface)
    if not matches:
        return None, None
    return matches.group(2), matches.group(3)


def normalize_interface(interface, include_module=True):
    module, port = parse_interface(interface)
    if not port:
        return None
    if include_module:
        return '%s.%s' % (module, port)
    else:
        return int(port)
