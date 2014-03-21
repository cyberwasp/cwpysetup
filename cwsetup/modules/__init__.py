__module_types = {}


def reg_module_type(module_type):
    __module_types[module_type.__name__] = module_type


def get_module_type(module_type_name):
    from .console import Console
    from .gui import Gui
    from .lib import Lib
    from .unknown import Unknown

    return __module_types[module_type_name]


def get_all_module_types():
    return __module_types.values()
