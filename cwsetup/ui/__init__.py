try:
    from . import gtk2ui
    UI = gtk2ui.Gtk2UI
except ImportError:
    try:
        from . import qt4ui
        UI = qt4ui.Qt4UI
    except ImportError:
        from . import qt5ui
        UI = qt5ui.Qt5UI



