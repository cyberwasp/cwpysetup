import cwsetup.installer
import cwsetup.modules.unknown
import PyQt4.QtGui


class Qt4UIWidget(PyQt4.QtGui.QWidget):
    def __init__(self):
        super(Qt4UIWidget, self).__init__()
        self.ok_button = PyQt4.QtGui.QPushButton("OK")
        self.cancel_button = PyQt4.QtGui.QPushButton("Cancel")
        self.table = PyQt4.QtGui.QTableWidget(self)
        self.hbox = PyQt4.QtGui.QHBoxLayout()
        self.vbox = PyQt4.QtGui.QVBoxLayout()
        self.init_ui()

    def init_ui(self):
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.ok_button)
        self.hbox.addWidget(self.cancel_button)

        self.vbox.addStretch(1)
        self.vbox.addWidget(self.table)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)

        self.setWindowTitle("Unknown modules setup config")
        sp = PyQt4.QtGui.QSizePolicy(PyQt4.QtGui.QSizePolicy.MinimumExpanding, PyQt4.QtGui.QSizePolicy.MinimumExpanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.setSizePolicy(sp)


class Qt4UI:
    def __init__(self, modules_):
        self.modules = list(modules_)
        self.app = PyQt4.QtGui.QApplication([])
        self.widget = Qt4UIWidget()

    def show(self):
        self.widget.cancel_button.clicked.connect(lambda x: self.app.exit(1))
        self.widget.ok_button.clicked.connect(lambda x: self.app.exit(0))
        table = self.widget.table
        table.setRowCount(len(self.modules))
        table.setColumnCount(2)
        for i in range(len(self.modules)):
            cmb = PyQt4.QtGui.QComboBox()
            for module_type in cwsetup.modules.get_all_module_types():
                    cmb.addItem(module_type.__name__)
            table.setItem(i, 0, PyQt4.QtGui.QTableWidgetItem(self.modules[i].get_name()))
            table.setItem(i, 1, PyQt4.QtGui.QTableWidgetItem(""))
            dcn = self.modules[i].get_display_class_name()
            idx = cmb.findText(dcn)
            cmb.setCurrentIndex(idx)
            table.setCellWidget(i, 1, cmb)
        self.widget.show()
        if self.app.exec_() == 0:
            for i in range(table.rowCount()):
                w = table.cellWidget(i, 1)
                if w.currentText() != cwsetup.modules.unknown.Unknown.__name__:
                    yield (str(table.item(i, 0).text()), str(w.currentText()))
        else:
            return


if __name__ == '__main__':
    from cwsetup.modules.gui import Gui
    from cwsetup.modules.unknown import Unknown
    modules = [Gui('aaaa', [], {}, {}, '', False, False), Unknown('bbbb', [], {}, {}, '', False, False)]
    ui = Qt4UI(modules)
    res = ui.show()
    for r in res:
        print(r)

