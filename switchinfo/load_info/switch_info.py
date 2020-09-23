import re
from pprint import pprint

from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.models import Switch


def switch_info(ip=None, community=None, device=None, silent=True):
    if not device:
        device = SwitchSNMP(community=community, device=ip)
    else:
        ip = device.device
        community = device.community
    info = device.switch_info()
    if not info:
        return

    switch, new = Switch.objects.get_or_create(ip=ip)
    switch.community = community
    switch.type = switch_type(info['descr'])
    switch.name = info['name'].split('.')[0]
    switch.description = info['descr']
    switch.location = info['location']

    if 'model' in info and not info['model'] == '':
        switch.model = info['model']
    else:
        switch.model = model_from_description(device, switch.type)

    switch.series = switch_series(switch)

    if not silent:
        pprint(info)
        print('Type: %s' % switch.type)
        print('Series: %s' % switch.series)
        print(switch.model)

    switch.save()
    return switch


def switch_type(description: str) -> str:
    if description.find('Cisco') == 0:
        return 'Cisco'
    elif description.find('ExtremeXOS') == 0:
        return 'Extreme'
    elif description.find('Aruba') == 0 or description.find('J9624A') > -1:
        return 'Aruba'
    elif description.find('ProCurve') == 0 or description.find('Formerly ProCurve') > -1:
        return 'ProCurve'
    elif description.find('Hewlett-Packard') == 0 or description.find('HP') == 0:
        return 'HP'
    elif description.find('Westermo') == 0:
        return 'Westermo'
    elif description.find('3Com') == 0:
        return '3Com'


def switch_series(switch):
    series = None
    if switch.type == 'Cisco':
        series = re.match(r'((?:WS|IE)-[A-Z0-9]+).*?$', switch.model)
    elif switch.type == 'Aruba':
        series = re.match(r'Aruba [A-Z0-9]+ ([A-Z0-9]+)', switch.description)

    if series:
        return series.group(1)


def model_from_description(device: SwitchSNMP, sw_type: str):
    description = device.create_list(oid='.1.3.6.1.2.1.47.1.1.1.1.2')  # ENTITY-MIB::entPhysicalDescr

    for string in description:
        if sw_type == 'Aruba':
            matches = re.match(r'Aruba [A-Z0-9]+\s(.+)\sSwitch', string)
        elif sw_type == 'Cisco':
            matches = re.match(r'Cisco.+?((:WS\-)?[cC][A-Z0-9\-]+).*switch', string, flags=re.DOTALL)
        elif sw_type == 'HP':
            matches = re.match(r'HP ([0-9\-]+) Switch Software', string)
        else:
            return None  # Unsupported type

        if matches:
            return matches.group(1)
