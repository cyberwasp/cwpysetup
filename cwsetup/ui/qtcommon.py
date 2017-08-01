import cwsetup.installer
import cwsetup.modules

def create(widget_module):

    class QtUIWidget(widget_module.QWidget):
        def __init__(self):
            super(QtUIWidget, self).__init__()
            self.ok_button = widget_module.QPushButton("OK")
            self.cancel_button = widget_module.QPushButton("Cancel")
            self.table = widget_module.QTableWidget(self)
            self.hbox = widget_module.QHBoxLayout()
            self.vbox = widget_module.QVBoxLayout()
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
            sp = widget_module.QSizePolicy(widget_module.QSizePolicy.MinimumExpanding, widget_module.QSizePolicy.MinimumExpanding)
            sp.setHorizontalStretch(0)
            sp.setVerticalStretch(0)
            self.setSizePolicy(sp)
    
    
    class QtUI:
        def __init__(self, modules_):
            self.modules = list(modules_)
            self.app = widget_module.QApplication([])
            self.widget = QtUIWidget()
    
        def show(self):
            self.widget.cancel_button.clicked.connect(lambda x: self.app.exit(1))
            self.widget.ok_button.clicked.connect(lambda x: self.app.exit(0))
            table = self.widget.table
            table.setRowCount(len(self.modules))
            table.setColumnCount(2)
            for i in range(len(self.modules)):
                cmb = widget_module.QComboBox()
                for module_type in cwsetup.modules.get_all_module_types():
                        cmb.addItem(module_type.__name__)
                table.setItem(i, 0, widget_module.QTableWidgetItem(self.modules[i].get_name()))
                table.setItem(i, 1, widget_module.QTableWidgetItem(""))
                dcn = self.modules[i].get_display_class_name()
                idx = cmb.findText(dcn)
                cmb.setCurrentIndex(idx)
                table.setCellWidget(i, 1, cmb)
            self.widget.show()
            if self.app.exec_() == 0:
                for i in range(table.rowCount()):
                    w = table.cellWidget(i, 1)
                    if w.currentText() != cwsetup.modules.Unknown.__name__:
                        yield (str(table.item(i, 0).text()), str(w.currentText()))
            else:
                return
    return QtUI