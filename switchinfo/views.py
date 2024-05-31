import urllib.parse
from pprint import pprint
from urllib.parse import unquote

from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render, resolve_url

from .forms import SearchForm
from .models import Arp, Interface, Mac, Switch, SwitchGroup, Vlan


def show_switch(request, name=None, ip=None):
    # switch = Switch.objects.get(name=name)
    if name:
        try:
            switch = get_object_or_404(Switch, name=unquote(name))
        except Switch.MultipleObjectsReturned:
            context = {'switches': Switch.objects.filter(name=name),
                       'title': name,
                       'ip_link': True}
            return render(request, 'switchinfo/switches.html', context)

    elif ip:
        switch = get_object_or_404(Switch, ip=ip)
    else:
        return
    interfaces = Interface.objects.filter(switch=switch)
    context = {
        'switch': switch,
        'interfaces': interfaces,
        'title': str(switch),
    }

    if switch.has_backup() and hasattr(settings, 'BACKUP_WEB_BASE'):
        context['backup_web_base'] = settings.BACKUP_WEB_BASE

    return render(request, 'switchinfo/switch.html', context)


def switch_json(request, name):
    switch = get_object_or_404(Switch, name=unquote(name))
    data = {
        'ip': switch.ip,
        'name': switch.name,
        'description': switch.description,
        'model': switch.model,
        'interfaces': {},
    }
    for interface in switch.interfaces.all():
        if interface.vlan_id:
            vlan = interface.vlan.vlan
        else:
            vlan = None
        data['interfaces'][interface.index] = {
            'name': interface.interface,
            'untagged_vlan': vlan,
            'tagged_vlans': list(interface.tagged_vlans.values_list('vlan', flat=True)),
            'description': interface.description,
            'mac': list(interface.macs.values_list('mac', flat=True)),
            'neighbor_string': interface.neighbor_string,
        }
    return JsonResponse(data)


def switches(request):
    switches_obj = Switch.objects.all()
    model = request.GET.get('model')
    series = request.GET.get('series')

    title = 'Switches'
    if model:
        switches_obj = switches_obj.filter(model__iexact=model)
        title += ' of type %s' % switches_obj.first().model
    if series:
        switches_obj = switches_obj.filter(series__iexact=series)
        title += ' in series %s' % switches_obj.first().series

    context = {
        'switches': switches_obj,
        'title': title,
    }
    return render(request, 'switchinfo/switches.html', context)


def switches_group(request):
    groups = dict()
    switches_nogroup = Switch.objects.all()
    db_groups = SwitchGroup.objects.all()
    group: SwitchGroup
    for group in db_groups:
        for switch in group.members():
            if group.name not in groups:
                groups[group.name] = []
            groups[group.name].append(switch)
        switches_nogroup = switches_nogroup.exclude(name__istartswith=group.grouping_key)
    groups[None] = switches_nogroup

    context = {
        'groups': groups.items(),
        'title': 'Switch groups',
    }
    return render(request, 'switchinfo/switches_group.html', context)


def vlan_ports(request, vlan):
    vlan_object = get_object_or_404(Vlan, vlan=vlan)
    switches_with_vlan = []
    for switch_object in vlan_object.on_switch.all():
        interfaces = switch_object.interfaces_in_vlan(vlan_object)
        switches_with_vlan.append([switch_object, interfaces])

    context = {
        'vlans': vlan_object,
        'switches': switches_with_vlan,
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
        elif form.cleaned_data['neighbor']:
            return neighbor_search(request, neighbor=form.cleaned_data['neighbor'])
    else:
        return render(request, 'switchinfo/search.html', {'form': form, 'title': 'Search switches'})


def mac_search(request, mac):
    mac = mac.lower()
    macs = Mac.objects.filter(mac__startswith=mac).\
        order_by('interface__switch').order_by('interface__index')

    mac_switch = dict()
    for mac in macs:
        switch = mac.interface.switch
        if switch not in mac_switch:
            mac_switch[switch] = []
        mac_switch[switch].append(mac.interface)

    return render(request, 'switchinfo/vlan.html',
                  context={'switches': mac_switch.items(),
                           'title': 'MAC addresses starting with %s' % mac})


def neighbor_search(request, neighbor):
    interfaces = Interface.objects.filter(neighbor_string__icontains=neighbor)

    neighbor_switch = {}
    for interface in interfaces:
        switch = interface.switch
        if switch not in neighbor_switch:
            neighbor_switch[switch] = []
        neighbor_switch[switch].append(interface)

    return render(request, 'switchinfo/vlan.html',
                  context={'switches': neighbor_switch.items(),
                           'title': 'Neighbors containing %s' % neighbor})


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
    vlans_obj = Vlan.objects.filter(has_ports=True, vlan__gt=1)

    context = {
        'vlans': vlans_obj,
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
        query = urllib.parse.urlencode({'model': model})
    elif series:
        query = urllib.parse.urlencode({'series': series})
    else:
        return HttpResponseBadRequest('Model or series must be specified')
    url = resolve_url('switchinfo:switches') + '?' + query
    return redirect(url)


def vlans_on_switch(request, switch_name):
    switch = Switch.objects.get(name=switch_name)
    context = {
        'vlans': Vlan.objects.filter(on_switch=switch),
        'title': 'Vlans on %s' % switch_name,
        'switch_name': switch_name,
        'switch': switch,
    }

    if request.path[-3:] == 'txt':
        return render(request, 'switchinfo/vlans_cli.html', context, content_type='text/plain')
    else:
        return render(request, 'switchinfo/vlans_on_switch.html', context)


def hosts(request):
    switches_string = ''
    switch: Switch
    for switch in Switch.objects.all():
        switches_string += '%s %s\n' % (switch.ip, switch.name)
    return HttpResponse(switches_string)
