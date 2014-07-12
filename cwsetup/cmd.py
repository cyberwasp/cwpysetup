from __future__ import print_function
import os
import sys
import win32event

error_file = filter(lambda x: x.startswith('--error='), sys.argv)
if error_file:
    sys.stderr = open(error_file[0][8:], 'w')

output_file = filter(lambda x: x.startswith('--output='), sys.argv)
if output_file:
    sys.stdout = open(output_file[0][9:], 'w')

path = filter(lambda x: x.startswith('--path='), sys.argv)
if path:
    sys.path = path[0][7:].split(';')

import tempfile
import cwutil
import win32con
from cwsetup.installer import Installer
from win32com.shell import shellcon
from win32com.shell.shell import ShellExecuteEx


def run_as_admin():
    output_file = tempfile.mktemp()
    error_file = tempfile.mktemp()
    try:
        print("Running with high privileges")
        rc = ShellExecuteEx(hwnd=0,
                            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS + shellcon.SEE_MASK_NO_CONSOLE,
                            lpVerb="runas",
                            lpFile='python.exe',
                            lpParameters=' '.join(sys.argv[:] +
                                                  ['--output=' + output_file,
                                                   '--error=' + error_file,
                                                   '--path=' + ';'.join(sys.path)]),
                            nShow=win32con.SW_HIDE)

        ret = win32event.WaitForSingleObject(rc['hProcess'], 100)

        def read_output(of):
            f = of
            if not of:
                if os.path.exists(output_file):
                    global f
                    f = open(output_file, "r")
            if f:
                l = f.readline()
                while l:
                    print(l, end='', sep='')
                    l = f.readline()

            return f

        of = None

        try:
            while ret == win32event.WAIT_TIMEOUT:
                ret = win32event.WaitForSingleObject(rc['hProcess'], 100)
                of = read_output(of)
            else:
                of = read_output(of)
        finally:
            if of:
                of.close()

        sys.stderr.write(open(error_file, 'r').read())

        os.remove(error_file)
        os.remove(output_file)

    except Exception as e:
        print(e)


def real_install():
    return len(sys.argv) > 1 and "--install" in sys.argv[1]


def main():
    if not cwutil.win32_is_user_an_admin() and real_install():
        run_as_admin()
    else:
        setup = Installer("w:\\progs")
        setup.run(real_install())

