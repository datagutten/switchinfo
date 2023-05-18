import os


def get_file(snmp_file):
    """
    When running multiple tests in the same process something locks the community to the IP address
    This function generates a unique loopback address for the given file
    :param snmp_file:
    :return:
    """
    files = os.scandir(os.path.join(os.path.dirname(__file__), '..', '..', 'test_data', 'snmp_data'))
    key = 1
    for file in files:
        name, extension = os.path.splitext(file.name)
        if name == snmp_file:
            return name, '127.0.0.%d' % key
        key += 1
