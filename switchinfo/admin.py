from django.contrib import admin

# Register your models here.
from .models import *


class CNetFilter(admin.SimpleListFilter):
    title = 'C-net'
    parameter_name = 'cnet'

    def lookups(self, request, model_admin):
        cnets = []
        for vlan in Vlan.objects.all():
            mac = Mac.objects.filter(interface__vlan=vlan).first()
            if not mac:
                continue
            arp = Arp.objects.filter(mac=mac.mac).first()
            if not arp:
                continue
            cnet = arp.cnet()
            if cnet in cnets:
                continue
            cnets.append(cnet)
        print(cnets)
        cnets.sort()
        return zip(cnets, cnets)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ip__startswith=self.value())


class ArpAdmin(admin.ModelAdmin):
    list_display = ('ip', 'mac', 'vlan', 'cnet')
    list_filter = (CNetFilter,)


admin.site.register(Arp, ArpAdmin)


class SwitchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'ip', 'type', 'model')


admin.site.register(Switch, SwitchAdmin)


class SwitchGroupAdmin(admin.ModelAdmin):
    list_display = ('grouping_key', 'name')


admin.site.register(SwitchGroup, SwitchGroupAdmin)


class VlanAdmin(admin.ModelAdmin):
    list_display = ('vlan', 'name')


admin.site.register(Vlan, VlanAdmin)


class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('switch', 'interface', 'vlan', 'description', 'poe_status')
    readonly_fields = (['switch'])
    list_filter = ('switch', 'vlan')


admin.site.register(Interface, InterfaceAdmin)


class MacAdmin(admin.ModelAdmin):
    list_display = ('mac', 'switch', 'interface')
    readonly_fields = (['switch'])
    # fieldsets = (['mac'], ['interface'])


admin.site.register(Mac, MacAdmin)
admin.site.register(Oui)