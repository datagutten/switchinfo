import load_info
from tests.load_info.LoadInfoCommon import LoadInfoCommon
from switchinfo import models
from parameterized import parameterized


class LoadArpTestCase(LoadInfoCommon):
    @parameterized.expand(
        [['pfsense'], ['aruba'], ['extreme'], ['cisco']]
    )
    def testLoadArp(self, switch: str):
        switch_obj = self.get_switch(switch)
        load_info.load_arp(switch_obj)
        count = models.Arp.objects.all().count()
        self.assertGreater(count, 0)
