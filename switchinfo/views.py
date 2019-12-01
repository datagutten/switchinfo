import re
from pprint import pprint

from django.shortcuts import get_object_or_404, redirect, render, HttpResponse

from .forms import SearchForm
from .models import Arp, Switch, Interface, Vlan, Mac


def show_switch(request, name):
    # switch = Switch.objects.get(name=name)
    switch = get_object_or_404(Switch, name=name)
    interfaces = Interface.objects.filter(switch=switch)
    context = {
        'switch': switch,
        'interfaces': interfaces,
        'title': str(switch),
    }
    return render(request, 'switchinfo/switch.html', context)


def switches(request):
    context = {
        'switches': Switch.objects.all(),
        'title': 'Switches',
    }
    return render(request, 'switchinfo/switches.html', context)


def switches_group(request):
    devices = Switch.objects.all()
    groups = dict()
    groups[None] = []
    for switch in devices:
        # group = re.match(r'(\S+?)\-[A-Z0-9\-]+$', switch.name)
        group = re.match(r'(\S+?)\-[A-Z0-9\-]+$', switch.name)
        if group:
            group_name = group.group(1)
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(switch)
        else:
            groups[None].append(switch)
    context = {
        'groups': groups.items(),
        'title': 'Switches',
    }
    return render(request, 'switchinfo/switches_group.html', context)


def vlan(request, vlan):
    vlan_object = get_object_or_404(Vlan, vlan=vlan)
    switches = []
    for switch_object in vlan_object.on_switch.all():
        interfaces = switch_object.interfaces_in_vlan(vlan_object)
        switches.append([switch_object, interfaces])

    context = {
        'vlans': vlan_object,
        'switches': switches,
        'title': str(vlan_object),
    }
    return render(request, 'switchinfo/vlan.html', context)


def search_form(request):
    form = SearchForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data['mac']:
            # return mac_search(request, )
            return redirect('switchinfo:mac', mac=form.cleaned_data['mac'])
        elif form.cleaned_data['ip']:
            return redirect('switchinfo:ip', ip=form.cleaned_data['ip'])
            # return ip_search(request, form.cleaned_data['ip'])
    else:
        return render(request, 'switchinfo/search.html', {'form': form})


def mac_search(request, mac):
    from pprint import pprint
    # interfaces = Interface.objects.filter()
    mac = mac.lower()
    macs = Mac.objects.filter(mac__startswith=mac).\
        order_by('interface__switch').order_by('interface__index')
    mac_switch = dict()
    pprint(macs)
    for mac in macs:
        switch = mac.interface.switch
        if switch not in mac_switch:
            mac_switch[switch] = []
        mac_switch[switch].append(mac.interface)
    pprint(mac_switch)
    return render(request, 'switchinfo/vlan.html',
                  context={'switches': mac_switch.items(),
                           'title': 'MAC addresses starting with %s' % mac})


def ip_search(request, ip):
    results = Arp.objects.filter(ip__startswith=ip).order_by('ip')
    mac_switch = dict()
    for result in results:
        try:
            pprint(result)
            mac = Mac.objects.get(mac=result.mac)
            switch = mac.interface.switch
            if switch not in mac_switch:
                mac_switch[switch] = []
            mac_switch[switch].append(mac.interface)
        except Mac.DoesNotExist:
            continue
            # ('MAC %s not found on any switch' % result.mac)
    context = {'switches': mac_switch.items(),
               'title': 'IP addresses starting with %s' % ip}
    return render(request, 'switchinfo/vlan.html', context)


def vlans(request):
    # vlans = Vlan.objects.filter(on_switch__switch__interface__startswith=)
    vlans = Vlan.objects.filter(has_ports=True, vlan__gt=1)

    context = {
        'vlans': vlans,
        'title': 'Vlans',
    }
    return render(request, 'switchinfo/vlans.html', context)


def load_interfaces(request, switch_name):
    from switchinfo.load_info.load_interfaces import load_interfaces
    switch_obj = get_object_or_404(Switch, name=switch_name)
    load_interfaces(switch_obj)
    return redirect('switchinfo:switch', name=switch_name)


def load_mac(request, switch_name):
    from django.core.management import call_command
    output = ''
    call_command('load_mac', switch_name, stdout=output)
    # return HttpResponse(output)
    return redirect('switchinfo:switch', name=switch_name)


def models(request):
    model_count = dict()
    for switch in Switch.objects.exclude(model__isnull=True).order_by('model'):
        model = '%s %s' % (switch.type, switch.model)
        if model not in model_count:
            model_count[model] = {'type': switch.type,
                                  'model': switch.model,
                                  'count': 1}
        else:
            model_count[model]['count'] += 1

    series_count = dict()
    for switch in \
            Switch.objects.exclude(series__isnull=True).order_by('series'):
        series = '%s %s' % (switch.type, switch.series)
        if series not in series_count:
            series_count[series] = {'type': switch.type,
                                    'series': switch.series,
                                    'count': 1}
        else:
            series_count[series]['count'] += 1

    return render(request, 'switchinfo/models.html',
                  context={'models': model_count.values(),
                           'series': series_count.values(),
                           'title': 'Switch models'})


def switch_model(request, model=None, series=None):
    if model:
        devices = Switch.objects.filter(model=model)
        title = devices.first().model
    elif series:
        devices = Switch.objects.filter(series=series)
        title = devices.first().series
    else:
        raise AttributeError('Model or series must be specified')

    return render(request, 'switchinfo/switches.html',
                  context={'switches': devices,
                           'title': title})


def vlans_on_switch(request, switch_name):
    switch = Switch.objects.get(name=switch_name)
    context = {
        'vlans': Vlan.objects.filter(on_switch=switch),
        'title': 'Vlans on %s' % switch_name,
        'switch_name': switch_name,
        'switch': switch,
    }

    return render(request, 'switchinfo/vlans_on_switch.html', context)


def hosts(request):
    switches_string = ''
    for switch in Switch.objects.all():
        switches_string += '%s %s\n' % (switch.ip, switch.name)
    return HttpResponse(switches_string)