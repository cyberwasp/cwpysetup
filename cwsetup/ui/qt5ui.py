from cwsetup.ui import qtcommon
from cwsetup.ui import common
import PyQt5.QtWidgets

Qt5UI = qtcommon.create(PyQt5.QtWidgets)

if __name__ == '__main__':
    common.demo(Qt5UI)
