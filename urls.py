from django.urls import path

from . import views

app_name = 'switchinfo'
urlpatterns = [
    path('switch/<str:name>', views.switch, name='switch'),
    path('switch', views.switches, name='switches'),
    path('switches', views.switches, name='switches2'),
    path('vlan/<int:vlan>', views.vlan, name='vlan'),
    path('vlans', views.vlans, name='vlans'),
]
