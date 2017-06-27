try:
    import ui.gtk2ui
    UI = ui.gtk2ui.Gtk2UI
except ImportError:
    import ui.qt4ui
    UI = ui.qt4ui.Qt4UI


