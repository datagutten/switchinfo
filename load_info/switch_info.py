import re
from pprint import pprint

from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.models import Switch


def switch_info(ip=None, community=None, device=None):
    if not device:
        device = SwitchSNMP(community=community, device=ip)
    else:
        ip = device.device
        community = device.community
    info = device.switch_info()
    if not info:
        return
    switch, new = Switch.objects.get_or_create(ip=ip)

    pprint(info)
    switch.community = community
    switch.type = switch_type(info['descr'])
    print(switch.type)
    switch.name = info['name'].split('.')[0]
    switch.description = info['descr']

    if info['model'] == '':
        switch.model = model_from_description(device, switch.type)
    else:
        switch.model = info['model']
    print(switch.model)
    switch.save()
    return switch


def switch_type(descr):
    if descr.find('Cisco') == 0:
        return 'Cisco'
    elif descr.find('ExtremeXOS') == 0:
        return 'Extreme'
    elif descr.find('Aruba') == 0:
        return 'Aruba'
    elif descr.find('Hewlett-Packard'):
        return 'HP'


def model_from_description(device, switch_type):
    descr = device.create_list(oid='.1.3.6.1.2.1.47.1.1.1.1.2')  # ENTITY-MIB::entPhysicalDescr
    for string in descr:
        if switch_type == 'Aruba':
            matches = re.match(r'Aruba [A-Z0-9]+\s(.+)\sSwitch', string)
        elif switch_type == 'Cisco':
            matches = re.match(r'Cisco.+?((:WS\-)?[cC][A-Z0-9\-]+).*switch', string)
        elif switch_type == 'HP':
            matches = re.match(r'HP ([0-9\-]+) Switch Software', string)
        else:
            return None  # Unsupported type

        if matches:
            return matches.group(1)
