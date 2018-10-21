from django.contrib import admin

# Register your models here.
from .models import *


class ArpAdmin(admin.ModelAdmin):
    list_display = ('ip', 'mac')


admin.site.register(Arp, ArpAdmin)


class SwitchAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip')


admin.site.register(Switch, SwitchAdmin)


class VlanAdmin(admin.ModelAdmin):
    list_display = ('vlan', 'name')


admin.site.register(Vlan, VlanAdmin)


class InterfaceAdmin(admin.ModelAdmin):
    list_display = ('switch', 'interface', 'vlan', 'description', 'poe_status')


admin.site.register(Interface, InterfaceAdmin)


class MacAdmin(admin.ModelAdmin):
    list_display = ('mac', 'switch', 'interface')
    readonly_fields = (['switch'])
    # fieldsets = (['mac'], ['interface'])


admin.site.register(Mac, MacAdmin)
admin.site.register(Oui)