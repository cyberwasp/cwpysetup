import cwsetup.installer
import cwsetup.modules.unknown
import PyQt5.QtWidgets

class Qt5UIWidget(PyQt5.QtWidgets.QWidget):
    def __init__(self):
        super(Qt5UIWidget, self).__init__()
        self.ok_button = PyQt5.QtWidgets.QPushButton("OK")
        self.cancel_button = PyQt5.QtWidgets.QPushButton("Cancel")
        self.table = PyQt5.QtWidgets.QTableWidget(self)
        self.hbox = PyQt5.QtWidgets.QHBoxLayout()
        self.vbox = PyQt5.QtWidgets.QVBoxLayout()
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
        sp = PyQt5.QtWidgets.QSizePolicy(PyQt5.QtWidgets.QSizePolicy.MinimumExpanding,
                                         PyQt5.QtWidgets.QSizePolicy.MinimumExpanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        self.setSizePolicy(sp)


class Qt5UI:
    def __init__(self, modules_):
        self.modules = list(modules_)
        self.app = PyQt5.QtWidgets.QApplication([])
        self.widget = Qt5UIWidget()

    def show(self):
        self.widget.cancel_button.clicked.connect(lambda x: self.app.exit(1))
        self.widget.ok_button.clicked.connect(lambda x: self.app.exit(0))
        table = self.widget.table
        table.setRowCount(len(self.modules))
        table.setColumnCount(2)
        for i in range(len(self.modules)):
            cmb = PyQt5.QtWidgets.QComboBox()
            for module_type in cwsetup.modules.get_all_module_types():
                    cmb.addItem(module_type.__name__)
            table.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(self.modules[i].get_name()))
            table.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(""))
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
    ui = Qt5UI(modules)
    res = ui.show()
    for r in res:
        print(r)

