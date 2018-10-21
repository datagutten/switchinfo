from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
from django.http import HttpResponse
from .models import Switch, Interface, Vlan
from pprint import pprint


def switch(request, name):
    switch = Switch.objects.get(name=name)
    interfaces = Interface.objects.filter(switch=switch)
    context = {
        'switch': switch,
        'interfaces': interfaces,
        'title': str(switch),
    }
    return render(request, 'switchinfo/switch.html', context)


def switches(request):
    switches = Switch.objects.all()
    context = {
        'switches': switches,
        'title': 'Switches',
    }
    return render(request, 'switchinfo/switches.html', context)


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
    #switches = Switch.objects.filter(has_vlan)


def vlans(request):
    # vlans = Vlan.objects.filter(on_switch__switch__interface__startswith=)
    vlans = Vlan.objects.filter(has_ports=True, vlan__gt=1)

    context = {
        'vlans': vlans,
        'title': 'Vlans',
    }
    return render(request, 'switchinfo/vlans.html', context)
