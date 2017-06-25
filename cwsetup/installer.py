import functools
import os
import shutil
import cwutil
import winshell
from config import Config
import cwsetup


class Installer(object):
    def __init__(self, root_dir):
        self.env = {}
        self.links = []
        self.path = cwutil.get_win32_all_user_env('PATH', False).split(';')
        self.root_dir = root_dir
        self.cfg = Config(root_dir)

    def delete_obsolete_path(self):
        path = list(self.path)
        for p in path:
            if p.upper().startswith(self.root_dir.upper()):
                self.path.remove(p)

    def setup_path(self, real=False):
        print '*' * 50
        print 'PATH'
        print '*' * 50
        for path in self.path:
            print path
        if real:
            cwutil.set_win32_all_user_env('PATH', ";".join(self.path))

    def make_links(self, real=False):
        print '*' * 50
        print 'LINKS'
        print '*' * 50
        for link in self.links:
            if os.path.exists(link.get("target")):
                print link
            else:
                print "Not exists: " + str(link)

        if real:
            links_dir = os.path.join(self.root_dir, cwsetup.config.LINKS_DIR)
            shutil.rmtree(links_dir, True)
            if not os.path.exists(links_dir):
                os.mkdir(links_dir)
            for link in self.links:
                target = link["target"]
                target_name, target_ext = os.path.splitext(os.path.basename(target))
                if target_ext.lower() == '.lnk':
                    shutil.copy(target, links_dir)
                else:
                    name = os.path.join(links_dir, link.get("name", target_name) + '.lnk')
                    winshell.CreateShortcut(Path=name, Target=target)

    def setup_env(self, real=False):
        print '*' * 50
        print 'ENV'
        print '*' * 50
        for e in self.env:
            print e + ' = ' + self.env[e]
        if real:
            for e in self.env:
                cwutil.set_win32_all_user_env(e, self.env[e])


    def run(self, real):
        self.delete_obsolete_path()
        self.cfg.refine_unknowns()
        for module in self.cfg.modules():
            if module.need_path:
                self.path += module.get_path()
            self.links += module.get_links()
            self.env.update(module.get_env())
        self.path = functools.reduce(lambda acc, x: (acc + [x]) if not x in acc else acc, self.path, [])
        self.setup_path(real)
        self.make_links(real)
        self.setup_env(real)

