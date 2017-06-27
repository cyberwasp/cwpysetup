import os
import cwsetup.installer
from cwsetup.modules.unknown import Unknown

os.environ['PATH'] = r'w:\progs\gtk\2.24.10\bin;' + os.environ['PATH']

import gtk


class Gtk2UI:
    def __init__(self, modules_):
        self.modules = list(modules_)

    def create_model(self):
        model = gtk.ListStore(str, str)
        for m in self.modules:
            model.append([m.get_name(), m.get_display_class_name()])
        return model

    def create_tree_view(self, model):

        def create_column_module_name():
            cell = gtk.CellRendererText()
            column = gtk.TreeViewColumn('Module')
            column.pack_start(cell, False)
            column.add_attribute(cell, 'text', 0)
            return column

        def create_column_module_type():
            def combo_changed(_, path, text, model):
                model[path][1] = text

            cell = gtk.CellRendererCombo()
            combo_model = gtk.ListStore(str)
            for module_type in cwsetup.modules.get_all_module_types():
                combo_model.append([module_type.__name__])

            cell.set_property("model", combo_model)
            cell.set_property("editable", True)
            cell.set_property("text-column", 0)
            cell.set_property("has-entry", False)
            cell.connect("edited", combo_changed, model)

            column = gtk.TreeViewColumn('Type')
            column.pack_start(cell, True)
            column.add_attribute(cell, 'text', 1)
            return column

        tree_view = gtk.TreeView(model)
        tree_view.append_column(create_column_module_name())
        tree_view.append_column(create_column_module_type())
        return tree_view

    def create_button(self, caption, ret):

        def set_exit_code(_, data):
            global exit_code
            exit_code = data
            gtk.main_quit()

        button = gtk.Button()
        button.set_label(caption)
        button.show()
        button.connect('clicked', set_exit_code, ret)
        return button

    def create_window(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Unknown modules setup config")
        window.set_size_request(400, 400)
        return window

    def show(self):
        exit_code = 0

        # create model
        model = self.create_model()

        # create views
        window = self.create_window()
        tree_view = self.create_tree_view(model)
        button_ok = self.create_button('Ok', 0)
        button_cancel = self.create_button('Cancel', 1)

        # make layout
        vbox = gtk.VBox()
        hbox = gtk.HBox(homogeneous=True)
        hbox.pack_start(button_ok, True)
        hbox.pack_start(button_cancel, True)
        vbox.pack_start(hbox, False)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.add(tree_view)
        vbox.pack_start(scrolled_window, True)
        window.add(vbox)

        window.show_all()

        gtk.main()

        if exit_code == 0:
            return [(row[0], row[1]) for row in model if row[1] != Unknown.__name__]
        else:
            return []


if __name__ == '__main__':
    from cwsetup.modules.gui import Gui

    modules = [Gui('aaaa', [], {}, {}, '', False, False), Unknown('bbbb', [], {}, {}, '', False, False)]
    ui = Gtk2UI(modules)
    res = ui.show()
    for r in res:
        print(r)
