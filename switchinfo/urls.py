from django.urls import path

from . import views

app_name = 'switchinfo'
urlpatterns = [
    path('switch/<str:switch_name>/load_interfaces', views.load_interfaces,
         name='switch_load_interfaces'),
    path('switch/<str:switch_name>/load_mac', views.load_mac,
         name='switch_load_mac'),
    path('switch/ip/<str:ip>', views.show_switch, name='switch'),
    path('switch/<str:name>', views.show_switch, name='switch'),
    path('switch/<str:switch_name>/vlans', views.vlans_on_switch, name='switch_vlans'),
    path('', views.switches, name='switches_index'),
    path('switch', views.switches, name='switches'),
    path('switches', views.switches, name='switches2'),
    path('switches/group', views.switches_group, name='groups'),
    path('vlan/<int:vlan>', views.vlan_ports, name='vlan'),
    path('vlans', views.vlans, name='vlans'),
    path('models', views.models, name='models'),
    path('model/<str:model>', views.switch_model, name='switch_model'),
    path('series/<str:series>', views.switch_model, name='switch_series'),
    path('search', views.search_form, name='search'),
    path('mac/<str:mac>', views.mac_search, name='mac'),
    path('ip/<str:ip>', views.ip_search, name='ip'),
    path('hosts', views.hosts, name='hosts'),
]
