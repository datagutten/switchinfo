import os.path
import re

from django.apps import apps
from django.conf import settings
from django.db import models

if hasattr(settings, 'TRUNK_FORCE_MAC'):
    trunk_force_mac = settings.TRUNK_FORCE_MAC
else:
    trunk_force_mac = ['Mitel IP Phone']


class Switch(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    ip = models.GenericIPAddressField()
    has_poe = models.BooleanField(default=False)
    type = models.CharField(max_length=50, blank=True, null=True)
    community = models.CharField(max_length=50, default='Public')
    model = models.CharField(max_length=100, blank=True, null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'switches'

    def __str__(self):
        return '%s (%s)' % (self.name, self.ip)

    def interfaces_in_vlan(self, vlan):
        return Interface.objects.filter(switch=self, vlan=vlan)

    def shorten_interface_name(self, interface_name: str):
        interface_name = str(interface_name)
        if self.type == 'Cisco':
            if interface_name.find('TwentyFiveGigE') == 0:
                return interface_name.replace('TwentyFiveGigE', 'Twe')
            else:
                return re.sub(r'([A-Z][a-z])[a-zA-Z]*([0-9\/]+)', r'\1\2',
                              interface_name)
        elif self.type == 'Extreme':
            return re.sub(r'Slot:\s+([0-9]+), Port:\s+([0-9]+)', r'\1:\2',
                          interface_name)
        else:
            return interface_name

    def vlans(self):
        return self.vlan.filter(vlan__gt=1)

    def has_backup(self):
        if hasattr(settings, 'BACKUP_PATH'):
            backup_path = os.path.join(settings.BACKUP_PATH + '/' + self.name)
            return os.path.exists(backup_path)

    def has_tree(self):
        if apps.is_installed('switch_tree'):
            from switch_tree.models import Tree
            try:
                Tree.objects.get(switch=self)
                return True
            except Tree.DoesNotExist:
                return False

    def neighbor_interfaces(self):
        """
        Get interfaces with neighbors
        :return:
        """
        return self.interfaces.exclude(neighbor=None)

    def software(self):
        matches = None
        if self.type == 'Aruba' or self.type == 'ProCurve':
            matches = re.search(r'revision ([A-Z]+[0-9.]+)', self.description)
        elif self.type == 'Aruba CX':
            matches = re.search(r'([A-Z]{2}\.[\d.]+)', self.description)
        elif self.type == 'HP':
            matches = re.search(r'Release ([A-Z0-9]+)', self.description)
        elif self.type in ['Cisco', 'Cisco IOS', 'Cisco IOS XE']:
            matches = re.search(r'Version ([\w.()]+)', self.description)
        elif self.type == 'Extreme':
            matches = re.search(r'version ([\d.]+)', self.description)

        if matches:
            return matches.group(1)


class SwitchGroup(models.Model):
    grouping_key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def members(self):
        return Switch.objects.filter(name__istartswith=self.grouping_key)

    def switches(self):
        items = []
        for group in SwitchGroup.objects.filter(name=self.name):
            items += group.members()
        return items


class Vlan(models.Model):
    vlan = models.IntegerField(unique=True)
    on_switch = models.ManyToManyField(Switch, related_name='vlan')
    name = models.CharField(max_length=50, blank=True, null=True)
    has_ports = models.BooleanField(default=False)

    class Meta:
        ordering = ['vlan']

    #    unique_together = (('switch', 'vlan'),)

    def __str__(self):
        if self.name:
            return '%s (%d)' % (self.name, self.vlan)
        else:
            return str(self.vlan)


class Interface(models.Model):
    index = models.IntegerField()
    switch = models.ForeignKey(
        Switch,
        on_delete=models.CASCADE,
        related_name='interfaces'
    )
    interface = models.CharField(max_length=50)
    type = models.CharField('Interface type', max_length=50)
    vlan = models.ForeignKey(
        Vlan,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='untagged_vlan')
    tagged_vlans = models.ManyToManyField(Vlan,
                                          related_name='tagged_vlans',
                                          blank=True)
    description = models.CharField(
        'User defined description for the interface',
        max_length=200, blank=True, null=True)
    status = models.IntegerField(null=True)
    admin_status = models.IntegerField(null=True)
    speed = models.BigIntegerField(blank=True, null=True)
    poe_status = models.CharField(max_length=50, blank=True, null=True)
    link_status_changed = models.DateField(null=True, blank=True)
    neighbor = models.ForeignKey(
        Switch, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='neighbor')
    neighbor_string = models.CharField(
        max_length=500,
        blank=True, null=True)
    neighbor_set_by = models.ForeignKey(
        Switch,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='neighbor_set_by')
    skip_mac = models.BooleanField(
        help_text='Do not load MAC-addresses for this interface',
        default=False)
    force_mac = models.BooleanField(
        help_text='Load MAC addresses even if the interface is trunk',
        default=False)
    aggregation = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='aggregation_members',
        help_text='Aggregation virtual interface',
    )

    class Meta:
        unique_together = (('switch', 'index'),)
        ordering = ['index']

    def mac(self):
        macs = Mac.objects.filter(interface=self)
        return macs

    def ip(self):
        ip = []
        for mac in self.mac():
            arp = Arp.objects.filter(mac=mac.mac)
            if arp.count() == 0:
                ip.append(None)
                continue

            ip.append(arp[0].ip)
        return ip

    def status_format(self):
        status = {1: 'up',
                  2: 'down',
                  3: 'testing',
                  4: 'unknown',
                  5: 'dormant',
                  6: 'notPresent',
                  7: 'lowerLayerDown'}

        if self.status in status:
            return status[self.status]

    def speed_format(self):
        if not self.speed:
            return 'auto'
        # speed = int(int(self.speed)/1000000)
        speed = self.speed
        if speed < 1000:
            speed = '%dM' % speed
        else:
            speed = '%dG' % int(speed / 1000)
        return speed

    def css(self):
        # if self.link_status_changed # cellUnused

        if self.status == 1:
            # if not self.description:
            #    return 'cellWarning'
            # else:
            return 'cellActive'
        else:
            return 'cellDefault'

    def switch_string(self):
        return '%s on %s' % (self.interface, self.switch)

    def is_trunk(self):
        if self.tagged_vlans.count() > 0 or self.vlan is None:
            return True
        else:
            return False

    def __str__(self):
        return self.interface


class Mac(models.Model):
    interface = models.ForeignKey(
        Interface,
        on_delete=models.CASCADE,
        related_name='macs'
    )
    mac = models.CharField(max_length=12)
    last_seen = models.DateTimeField(auto_now=False, blank=True, null=True)

    def switch(self):
        return self.interface.switch

    def ip(self):
        return Arp.objects.get(mac=self.mac)

    def __str__(self):
        return self.mac

    def oui(self):
        prefix = self.mac[0:6]
        prefix = prefix.upper()

        prefix_info = Oui.objects.filter(prefix=prefix)
        if prefix_info.count() > 0:
            return prefix_info.first().vendor
        else:
            return ''


class Arp(models.Model):
    mac = models.CharField(max_length=12, unique=True, primary_key=True)
    ip = models.GenericIPAddressField()

    def __str__(self):
        return '%s %s' % (self.mac, self.ip)

    def vlan(self):
        mac_obj = Mac.objects.get(mac=self.mac)
        return mac_obj.interface.vlan

    def cnet(self):
        import re
        return re.sub(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\.[0-9]{1,3}', r'\1', self.ip)


class Oui(models.Model):
    prefix = models.CharField(max_length=6)
    vendor = models.CharField(max_length=100)

    def __str__(self):
        return self.prefix + ' ' + self.vendor
