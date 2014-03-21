from unittest import TestCase
from cwsetup.modules.module import module_types

class TestModules(TestCase):

    def test_regs(self):
        print(module_types)
        self.assertTrue(len(module_types) > 1)



