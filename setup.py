from _winreg import CloseKey, OpenKey, QueryValueEx, SetValueEx, \
    HKEY_LOCAL_MACHINE, KEY_READ, KEY_ALL_ACCESS, REG_EXPAND_SZ
from inspect import isclass
from tempfile import mktemp
from win32com.shell import shellcon
from win32com.shell.shell import ShellExecuteEx
from win32gui import SendMessage
import gtk
import imp
import os
import shutil
import sys
import win32con
import winshell


ENV_REG_PATH = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
LINKS_DIR = '.links'
CFG_FILE_NAME = 'setup_cfg.py'

def isadmin():
    try:
        key = OpenKey(HKEY_LOCAL_MACHINE, ENV_REG_PATH, 0, KEY_ALL_ACCESS)
        CloseKey(key)
        return True
    except:
        return False

def runasadmin():
    try:
        rc = ShellExecuteEx(hwnd=0,
                        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS + shellcon.SEE_MASK_NO_CONSOLE,
                        lpVerb="runas",
                        lpFile='python.exe',
                        lpParameters=' '.join(sys.argv[:]),
                        nShow=win32con.SW_SHOW)
    except Exception as e:
        print "Exit code: " + str(rc)
        print e[2]
        sys.exit()

def get_env(name):
    key = OpenKey(HKEY_LOCAL_MACHINE, ENV_REG_PATH, 0, KEY_READ)
    value, _ = QueryValueEx(key, name)
    CloseKey(key)
    return value

def set_env(name, value):
    key = OpenKey(HKEY_LOCAL_MACHINE, ENV_REG_PATH, 0, KEY_ALL_ACCESS)
    SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
    CloseKey(key)
    SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')

class Setup(object):
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.modules = []
        self.unknown_modules = []
        for module_root_dir in sorted(filter(os.path.isdir, map(lambda x: os.path.join(self.root_dir, x), os.listdir(self.root_dir)))):
            cfg_file_name = os.path.join(module_root_dir, CFG_FILE_NAME)
            if os.path.exists(cfg_file_name):
                module = Module.new(cfg_file_name, os.path.join(root_dir, module_root_dir))
                #can ignore same dirs
                if module:
                    self.modules.append(module)
            else:
                if not os.path.basename(module_root_dir) in [LINKS_DIR]:
                    self.unknown_modules.append(module_root_dir) 
                
    def setup_cfgs(self):
        
        def column_module():
            cell = gtk.CellRendererText()
            column = gtk.TreeViewColumn('Module') 
            column.pack_start(cell, False)
            column.add_attribute(cell, 'text', 0)
            return column
            
        def column_type(m):
            
            def combo_changed(widget, path, text, model):
                model[path][1] = text
            
            cell = gtk.CellRendererCombo()
            combo_model = gtk.ListStore(str)
            for name, x in globals().iteritems():
                if isclass(x) and issubclass(x, Module) and x != Module:
                    combo_model.append([name])

            cell.set_property("model", combo_model) 
            cell.set_property("editable", True)
            cell.set_property("text-column", 0)
            cell.set_property("has-entry", False)
            cell.connect("edited", combo_changed, m)        
                    
            column = gtk.TreeViewColumn('Type') 
            column.pack_start(cell, True)
            column.add_attribute(cell, 'text', 1)
            return column
        
        def model():
            model = gtk.ListStore(str, str)
            for unknown_module in self.unknown_modules:
                model.append([os.path.basename(unknown_module), ""])
            return model
        
        def treeview(model):
            treeview = gtk.TreeView(model)
            treeview.append_column(column_module())
            treeview.append_column(column_type(model))
            return treeview
            
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("First setup config")
        window.set_size_request(400, 400) 

        model = model()
        
        treeview = treeview(model)
        
        exit_code = 0

        def set_exit_code(widget, data):
            global exit_code
            exit_code = data
            gtk.main_quit()

        button_ok = gtk.Button();
        button_ok.set_label("Ok")
        button_ok.show()
        button_ok.connect('clicked', set_exit_code, 0)
        
        button_cancel = gtk.Button();
        button_cancel.set_label("Cancel")
        button_ok.connect('clicked', set_exit_code, 1)
        button_cancel.show()
        
        vbox = gtk.VBox()
        hbox = gtk.HBox(homogeneous=True)
        hbox.pack_start(button_ok, True)
        hbox.pack_start(button_cancel, True)
        vbox.pack_start(hbox, False)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.add(treeview);
        vbox.pack_start(scrolled_window, True)
        
        window.add(vbox)
        window.show_all()
        
        gtk.main()
        
        if exit_code == 0:
            for row in model:
                name = row[0] 
                typee = row[1]
                if typee:
                    with open(os.path.join(self.root_dir, name, CFG_FILE_NAME), 'w') as f:
                        f.write('TYPE="' + typee + '"')
        return False    
    

    def delete_obsolete_path(self):
        path = list(self.path)
        for p in path:
            if p.upper().startswith(self.root_dir.upper()):
                self.path.remove(p)

    def setup_path(self, real = False):
        print '*' * 50
        print 'PATH'
        print '*' * 50
        for path in self.path:
            print path     
        if real:
            set_env('PATH', ";".join(self.path))
    
    def make_links(self, real = False):
        print '*' * 50
        print 'LINKS'
        print '*' * 50
        for link in self.links:
            print link     

        if real:
            links_dir = os.path.join(self.root_dir, LINKS_DIR)
            shutil.rmtree(links_dir, True)
            if not os.path.exists(links_dir):
                os.mkdir(links_dir)                
            for target in self.links:
                target_name, target_ext = os.path.splitext(os.path.basename(target))
                if target_ext.lower() == '.lnk':
                    shutil.copy(target, links_dir)
                else:                    
                    link = os.path.join(links_dir, target_name + '.lnk')
                    winshell.CreateShortcut(Path=link, Target=target)

    def setup_env(self, real = False):                
        print '*' * 50
        print 'ENV'
        print '*' * 50
        for e in self.env:
            print e + ' = ' + self.env[e]
        if real:
            for e in self.env:
                set_env(e, self.env[e])
            

    def run(self, real):
        self.path = get_env('PATH').split(';')
        self.delete_obsolete_path()
        self.links = []
        self.env = {}
        if not self.unknown_modules or (self.unknown_modules and self.setup_cfgs()):
            for module in self.modules:
                self.path += module.get_path()
                self.links += module.get_links()
                self.env.update(module.get_env())
            self.setup_path(real)
            self.make_links(real)
            self.setup_env(real)
        
class Module(object):
    
    def __init__(self, root_dir, path, links, env, main_exe_name, versioning):
        self.root_dir = root_dir
        self.path = path
        self.links = links
        self.env = env
        self.main_exe_name = main_exe_name
        self.versioning = versioning
        self.last_ver_dir = self.get_last_version_dir()
        
    @staticmethod    
    def new(cfg_file_name, module_root_dir):
        
        cfg_file_name_tmp = mktemp()
        shutil.copy(cfg_file_name, cfg_file_name_tmp)
        
        m = imp.load_source(os.path.basename(module_root_dir),  cfg_file_name_tmp)
        
        ignore = m.IGNORE if hasattr(m, 'IGNORE') else False
        
        if ignore: 
            return None
        
        if hasattr(m, 'TYPE'):
            typee = m.TYPE
        else:
            raise Exception('Unknown module type:' + cfg_file_name)

        versioning = m.VERSIONING if hasattr(m, 'VERSIONING') else True
        path = m.PATH if hasattr(m, 'PATH') else None
        links = m.LINKS if hasattr(m, 'LINKS') else None
        main_exe_name = m.EXE if hasattr(m, 'EXE') else None  
        env = m.ENV if hasattr(m, 'ENV') else None
        
        module = globals()[typee](module_root_dir, path, links, env, main_exe_name, versioning)
       
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
   
    def get_main_exe_name(self):
        if self.main_exe_name:
            return self.main_exe_name
        else:
            return os.path.basename(self.root_dir)
   
    def get_main_exe_full_name(self):    
        return os.path.join(self.get_last_version_dir(), self.get_main_exe_name() + '.exe') 
        

    def expand_strings_in_list(self, lst):
        for p in lst:
            try:
                yield p.format(**self.__dict__) 
            except:
                raise Exception("Error in string", p)
        
    def expand_strings_in_map(self, mp):
        r = {}
        for p in mp:
            try:
                val = mp[p].format(**self.__dict__) 
            except:
                raise Exception("Error in string", p)
            r[p] = val
        return r

    
    def get_path(self):
        if self.path:
            return self.expand_strings_in_list(self.path)
        else:
            return []
        
    def get_links(self):
        if self.links:
            return self.expand_strings_in_list(self.links)
        else:
            return []
        
    def get_env(self):
        if self.env:
            return self.expand_strings_in_map(self.env)
        else:
            return {}
        
    def setup(self, demo = True):
        pass
    
class Lib(Module):

    def get_path(self):
        if self.path != None:
            return self.path
        else:
            return [self.get_last_version_dir()]

class Gui(Module):

    def get_links(self):
        if self.links != None:
            return self.expand_strings_in_list(self.links)
        else:
            return self.expand_strings_in_list([self.get_main_exe_full_name()])
    
class Console(Module):
    
    def get_path(self):
        if self.path != None:
            return self.expand_strings_in_list(self.path)
        else:
            return self.expand_strings_in_list([self.get_last_version_dir()])

def real_install():
    return len(sys.argv) > 1 and  "--install" in sys.argv[1]


if __name__ == '__main__':
    if not isadmin() and real_install():
        runasadmin()
    else:
        setup = Setup("w:\\progs")
        setup.run(real_install())
