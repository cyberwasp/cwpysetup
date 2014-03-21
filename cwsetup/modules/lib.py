from cwsetup.modules.module import Module


class Lib(Module):
    def get_path(self):
        if self.path:
            return self.path
        else:
            return [self.get_last_version_dir()]
