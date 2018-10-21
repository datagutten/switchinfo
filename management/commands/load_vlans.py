from django.core.management.base import BaseCommand  # , CommandError

from switchinfo.models import Switch, Vlan
from switchinfo.SwitchSNMP.select import get_switch
from pprint import pprint


class Command(BaseCommand):
    help = 'Import vlans from switches'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['switch'][0]=='all':
            switches = Switch.objects.filter(name=options['switch'][0])
        else:
            switches = Switch.objects.all()
        for switch in switches:
            device = get_switch(switch)
            if not device:
                continue

            current_vlans = Vlan.objects.filter(on_switch=switch)
            vlan_names = device.vlan_names()
            # vlans on switch
            vlans_on_switch = device.vlans()

            if not vlans_on_switch:
                continue
            Vlan.objects.get_or_create(vlan=0, name='Trunk')
            for vlan in vlans_on_switch:
                vlan_obj, created = Vlan.objects.get_or_create(vlan=vlan)
                if created:
                    print ('Created vlan %d on switch %s' % (vlan, switch))
                # vlan name
                if str(vlan) in vlan_names:
                    vlan_name = vlan_names[str(vlan)]
                    if vlan_name.find('VLAN') < 0:
                        vlan_obj.name=vlan_name
                        vlan_obj.save()
                vlan_obj.on_switch.add(switch)
            # vlans in database
            for vlan in current_vlans:
                if vlan.vlan not in vlans_on_switch:
                    print ('Vlan %d not on switch %s' % (vlan.vlan, switch))
                    vlan.on_switch.remove(switch)
                    if not vlan.on_switch.all():
                        print ('Vlan %d not on any switches' % vlan.vlan)
                        vlan.delete()
                    else:
                        vlan.save()
