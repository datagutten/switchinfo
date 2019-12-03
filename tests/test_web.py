from django.test import TestCase
from django.test import Client

from switchinfo.load_info import switch_info

c = Client()


class WebTestCase(TestCase):
    def setUp(self):
        switch_info.switch_info('127.0.0.1', 'cisco')
        # switch_info.switch_info('127.0.0.1', 'cisco_16_switch')

    def test_frontPage(self):
        response = c.get('/')
        self.assertContains(response, 'Switches')
        self.assertContains(response, 'ROV-SW-01')

    def test_switch(self):
        response = c.get('/switch/ROV-SW-01')
        self.assertContains(response, '2960')

    def test_vlans(self):
        response = c.get('/vlans')
        self.assertContains(response, 'Vlans')

    def test_models(self):
        response = c.get('/models')
        self.assertContains(response, 'Switch models')
        self.assertContains(response, 'Cisco&nbsp;WS-C2960S-24PS-L')

    def test_switch_groups(self):
        response = c.get('/switches/group')
        self.assertContains(response, 'Switch groups')

    def test_search(self):
        response = c.get('/search')
        self.assertContains(response, 'Search switches')
