from django.test import TestCase
from django.test import Client

from switchinfo.load_info import switch_info
from switchinfo.models import Switch, Vlan

c = Client()


class WebTestCase(TestCase):
    def setUp(self):
        Switch(name='ROV-SW-01', ip='127.0.0.1', has_poe=True, type='Cisco',
               community='public', model='WS-C2960S-24PS-L',
               description='Cisco IOS Software, C2960S Software (C2960S-UNIVERSALK9-M), Version 15.0(2)SE11, RELEASE SOFTWARE (fc3)').save()

    def test_frontPage(self):
        response = c.get('/')
        self.assertContains(response, 'Switches')
        self.assertContains(response, 'ROV-SW-01')

    def test_switch(self):
        response = c.get('/switch/ROV-SW-01')
        self.assertContains(response, '2960')

    def test_vlans(self):
        switch = Switch.objects.get(ip='127.0.0.1')
        vl = Vlan(vlan=12, name='PC', has_ports=True)
        vl.save()
        vl.on_switch.add(switch)
        response = c.get('/vlans')

        self.assertContains(response, '<h1>Vlans</h1>')
        self.assertContains(response,
                            '<a href="/vlan/12">PC (12)</a>')

    def test_vlan(self):
        switch = Switch.objects.get(ip='127.0.0.1')
        vl = Vlan(vlan=12, name='PC', has_ports=True)
        vl.save()
        vl.on_switch.add(switch)
        response = c.get('/vlan/12')
        self.assertContains(response, '<h1>PC (12)</h1>')
        self.assertContains(response, '<a href="/switch/ROV-SW-01">ROV-SW-01 (127.0.0.1)</a>')

    def test_models(self):
        response = c.get('/models')
        self.assertContains(response, '<h1>Switch models</h1>')
        self.assertContains(response, 'Cisco&nbsp;WS-C2960S-24PS-L')

    def test_switch_groups(self):
        response = c.get('/switches/group')
        self.assertContains(response, '<h1>Switch groups</h1>')
        self.assertContains(response, '<h2>No group</h2>')

    def test_search(self):
        response = c.get('/search')
        self.assertContains(response, '<h1>Search switches</h1>')
