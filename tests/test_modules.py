from unittest import TestCase
from cwsetup.modules import get_all_module_types


class TestModules(TestCase):
    def test_regs(self):
        self.assertTrue(len(get_all_module_types()) > 1)



