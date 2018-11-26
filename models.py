from django.db import models


class Switch(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    ip = models.GenericIPAddressField()
    has_poe = models.BooleanField(default=False)
    type = models.CharField(max_length=50, blank=True, null=True)
    community = models.CharField(max_length=50, default='Public')
    model = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '%s (%s)' % (self.name, self.ip)

    def interfaces_in_vlan(self, vlan):
        return Interface.objects.filter(switch=self, vlan=vlan)

    def shorten_interface_name(self, interface_name):
        import re
        if self.type == 'Cisco':
            return re.sub(r'([A-Z][a-z]).+?([0-9\/]+)', r'\1\2',
                          interface_name)
        elif self.type == 'Extreme':
            return re.sub(r'Slot:\s+([0-9]+), Port:\s([0-9]+)', r'\1:\2',
                          interface_name)
        else:
            return interface_name


class Vlan(models.Model):
    vlan = models.IntegerField(unique=True)
    on_switch = models.ManyToManyField(Switch)
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
    switch = models.ForeignKey(Switch, on_delete=models.CASCADE,
                               related_name='switch')
    interface = models.CharField(max_length=50)
    vlan = models.ForeignKey(Vlan, on_delete=models.CASCADE,
                             blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    status = models.IntegerField(null=True)
    admin_status = models.CharField(max_length=50, blank=True, null=True)
    speed = models.BigIntegerField(blank=True, null=True)
    poe_status = models.CharField(max_length=50, blank=True, null=True)
    link_status_changed = models.DateField(null=True)
    neighbor = models.ForeignKey(Switch, on_delete=models.CASCADE,
                                 blank=True, null=True,
                                 related_name='neighbor')
    neighbor_string = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        unique_together = (('switch', 'interface'),)
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
            print (arp)
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
            speed = '%dG' % int(speed/1000)
        return speed

    def last_change_format(self):
        # last_change_seconds = int(self.last_change)/100
        # last_change_days = last_change_seconds/3600/24
        last_change_days = self.last_change/8640000
        return last_change_days

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

    def __str__(self):
        return self.interface


class Mac(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    mac = models.CharField(max_length=12)
    last_seen = models.DateTimeField(auto_now=False, blank=True, null=True)

    def switch(self):
        return self.interface.switch

    def __str__(self):
        return self.mac

    def oui(self):
        prefix = self.mac[0:6]
        prefix = prefix.upper()

        prefix_info = Oui.objects.filter(prefix=prefix)
        if prefix_info.count() > 0:
            print(prefix_info)
            return prefix_info.first().vendor
        else:
            return ''


class Arp(models.Model):
    mac = models.CharField(max_length=12)
    ip = models.GenericIPAddressField()

    def __str__(self):
        return '%s %s' % (self.mac, self.ip)


class Oui(models.Model):
    prefix = models.CharField(max_length=6)
    vendor = models.CharField(max_length=100)

    def __str__(self):
        return self.prefix + ' ' + self.vendor
