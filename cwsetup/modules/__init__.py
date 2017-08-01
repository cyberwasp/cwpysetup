from .console import Console
from cwsetup.modules.gui import Gui
from cwsetup.modules.lib import Lib
from cwsetup.modules.unknown import Unknown
from cwsetup.modules.module import Module

new = Module.new

def get_module_type(module_type_name):
    return next(iter(filter(lambda x: x.__name__ == module_type_name, get_all_module_types())))


def get_all_module_types():
    return [Console, Gui, Lib, Unknown]
