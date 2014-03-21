from cwsetup.modules.module import Module


class Console(Module):
    def get_path(self):
        if self.path:
            return self.expand_strings(self.path)
        else:
            return self.expand_strings([self.get_last_version_dir()])
