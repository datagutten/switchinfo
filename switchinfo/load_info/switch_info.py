import re
from pprint import pprint
from typing import Optional

from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.SwitchSNMP.exceptions import SNMPError
from switchinfo.models import Switch


def switch_info(ip: str = None, community: str = None, device: SwitchSNMP = None, silent=True) -> Optional[Switch]:
    if not device:
        device = SwitchSNMP(community=community, device=ip)
    else:
        ip = device.device
        community = device.community
    try:
        info = device.switch_info()
    except SNMPError as e:
        e.message = 'Unable to get switch info: %s' % e
        raise e

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

    if info['model'][0:3] == 'FSW':
        switch.type = 'Fortinet'

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
        version = re.search(r'Version (\d+)', description)
        if int(version.group(1)) >= 16:
            return 'Cisco IOS XE'
        else:
            return 'Cisco'
    elif description.find('ExtremeXOS') == 0:
        return 'Extreme'
    elif description.find('Aruba') == 0 or description.find('J9624A') > -1:
        if description.find('6100') > -1 or description.find('6200') > -1:
            return 'Aruba CX'
        else:
            return 'Aruba'
    elif description.find('ProCurve') > -1:
        return 'ProCurve'
    elif description.find('Comware') > -1:
        return 'Comware'
    elif re.search(r'Hewlett[-\s]Packard', description) or description.strip().find('HP') == 0:
        return 'HP'
    elif description.find('Westermo') == 0:
        return 'Westermo'
    elif description.find('3Com') == 0:
        return '3Com'
    elif description.find('Schneider') == 0:
        return 'Schneider'


def switch_series(switch: Switch) -> str:
    series = None
    if switch.type == 'Cisco':
        series = re.match(r'((?:WS|IE)-[A-Z0-9]+).*?$', switch.model)
    elif switch.type == 'Aruba':
        series = re.match(r'Aruba [A-Z0-9]+ ([A-Z0-9]+)', switch.description)
    elif switch.type == 'HP':
        series = re.search(r'HPE? (\w+)', switch.description)
    elif switch.type == 'ProCurve':
        series = re.search(r'ProCurve \w+ Switch (\w+)', switch.description) or re.search(r'HP \w+ (\w+)',
                                                                                          switch.description)

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
