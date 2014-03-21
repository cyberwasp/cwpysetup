from cwsetup.modules.module import Module


class Gui(Module):
    def get_links(self):
        if self.links:
            return self.expand_strings(self.links)
        else:
            return self.expand_strings([{"target": self.get_main_exe_full_name()}])

