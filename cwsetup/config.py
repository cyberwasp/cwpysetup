import os
import cwsetup.modules


LINKS_DIR = '.links'
ARCHIVE_DIR = '.archive'
CFG_FILE_NAME = 'setup_cfg.py'


class Config:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.__modules = {}

    def module_dirs(self):
        for elem in os.listdir(self.root_dir):
            may_be_module_dir = os.path.join(self.root_dir, elem)
            if os.path.isdir(may_be_module_dir) and elem != LINKS_DIR and elem != ARCHIVE_DIR:
                yield may_be_module_dir

    def modules(self):
        for x in self.module_dirs():
            if not x in self.__modules:
                cfg_file_name = os.path.join(x, CFG_FILE_NAME)
                module = cwsetup.modules.new(cfg_file_name, x)
                self.__modules[x] = module
            if self.__modules[x]:
                yield self.__modules[x]

    def get_unknowns(self):
        return filter(lambda x: isinstance(x, cwsetup.modules.Unknown), self.modules())

    def refine_unknowns(self):
        from cwsetup.ui import UI

        unknowns = list(self.get_unknowns())
        if unknowns:
            ui = UI(unknowns)
            res = ui.show()
            self.update_unknowns(res)

    def update_unknowns(self, refines):
        for module_name, module_type in refines:
            with open(os.path.join(self.root_dir, module_name, CFG_FILE_NAME), 'w') as f:
                f.write('TYPE="' + module_type + '"')