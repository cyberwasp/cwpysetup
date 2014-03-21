from cwsetup.modules.module import Module


class Unknown(Module):
    def get_path(self):
        return []

    def get_links(self):
        return []

    def get_env(self):
        return {}
