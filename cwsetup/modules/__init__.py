__module_types = {}


def reg_module_type(module_type):
    __module_types[module_type.__name__] = module_type


def get_module_type(module_type_name):
    return next(filter(lambda x: x.__name__ == module_type_name, get_all_module_types()))


def get_all_module_types():
    from .console import Console
    from .gui import Gui
    from .lib import Lib
    from .unknown import Unknown
    return [Console, Gui, Lib, Unknown]
