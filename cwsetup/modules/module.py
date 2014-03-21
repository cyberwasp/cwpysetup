import imp
import os
import shutil
from tempfile import mktemp
import cwsetup

def format_and_expand(formatted_string, params):
    ret = formatted_string.format(**params)
    ret = os.path.expandvars(ret)
    return os.path.expanduser(ret)


class ModuleType(type):
    def __init__(cls, name, bases, dict):
        if cls.__name__ != 'Module':
            cwsetup.modules.reg_module_type(cls)
        super(ModuleType, cls).__init__(cls)


class Module(object):
    __metaclass__ = ModuleType

    def __init__(self, root_dir, path, links, env, main_exe_name, versioning):
        self.root_dir = root_dir
        self.path = path
        self.links = links
        self.env = env
        self.main_exe_name = main_exe_name
        self.versioning = versioning
        self.last_ver_dir = self.get_last_version_dir()
        self.last_ver_home = self.get_last_version_home()

    @staticmethod
    def new(cfg_file_name, module_root_dir):

        cfg_file_name_tmp = mktemp()

        if os.path.exists(cfg_file_name):
            shutil.copy(cfg_file_name, cfg_file_name_tmp)
        else:
            with open(cfg_file_name_tmp, 'w') as f:
                f.write('TYPE="Unknown"')

        m = imp.load_source('cwsetup.configs.' + os.path.basename(module_root_dir), cfg_file_name_tmp)

        ignore = m.IGNORE if hasattr(m, 'IGNORE') else False

        if ignore:
            return None

        if hasattr(m, 'TYPE'):
            typee = m.TYPE
        else:
            raise Exception('Unknown module type:' + cfg_file_name)

        versioning = m.VERSIONING if hasattr(m, 'VERSIONING') else typee != 'Unknown'
        path = m.PATH if hasattr(m, 'PATH') else None
        links = m.LINKS if hasattr(m, 'LINKS') else None
        main_exe_name = m.EXE if hasattr(m, 'EXE') else None
        env = m.ENV if hasattr(m, 'ENV') else None

        import cwsetup

        module = cwsetup.modules.get_module_type(typee)(module_root_dir, path, links, env, main_exe_name, versioning)

        os.remove(cfg_file_name_tmp)

        if os.path.exists(cfg_file_name_tmp + 'c'):
            os.remove(cfg_file_name_tmp + 'c')

        if os.path.exists(cfg_file_name_tmp + 'o'):
            os.remove(cfg_file_name_tmp + 'o')

        return module

    def get_versions(self):
        if self.versioning:
            res = []
            for item in os.listdir(self.root_dir):
                if os.path.isdir(os.path.join(self.root_dir, item)):
                    res.append(item)
            return sorted(res)
        else:
            return None

    def get_last_version(self):
        versions = self.get_versions()
        return versions[-1] if versions else None

    def get_last_version_dir(self):
        last_version = self.get_last_version()
        path = self.root_dir if not last_version else os.path.join(self.root_dir, self.get_last_version())
        bin_path = os.path.join(path, 'bin')
        if os.path.exists(bin_path) and os.path.isdir(bin_path):
            path = bin_path
        return path

    def get_last_version_home(self):
        last_version = self.get_last_version()
        path = self.root_dir if not last_version else os.path.join(self.root_dir, self.get_last_version())
        return path

    def get_main_exe_name(self):
        if self.main_exe_name:
            return self.main_exe_name
        else:
            return os.path.basename(self.root_dir)

    def get_main_exe_full_name(self):
        return os.path.join(self.get_last_version_dir(), self.get_main_exe_name() + '.exe')

    def expand_strings(self, data):
        if isinstance(data, {}.__class__):
            return self.expand_strings_in_map(data)
        elif isinstance(data, [].__class__):
            return self.expand_strings_in_list(data)
        elif isinstance(data, "".__class__):
            return format_and_expand(data, self.__dict__)
        else:
            return data

    def expand_strings_in_list(self, lst):
        for p in lst:
            try:
                yield self.expand_strings(p)
            except Exception as e:
                raise Exception("Error in string", p, e)

    def expand_strings_in_map(self, mp):
        r = {}
        for p in mp:
            try:
                val = self.expand_strings(mp[p])
            except:
                raise Exception("Error in string", p)
            r[p] = val
        return r

    def get_path(self):
        if self.path:
            return self.expand_strings(self.path)
        else:
            return []

    def get_links(self):
        if self.links:
            return self.expand_strings(self.links)
        else:
            return []

    def get_env(self):
        if self.env:
            return self.expand_strings(self.env)
        else:
            return {}


