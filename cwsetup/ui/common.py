from cwsetup.modules import Gui, Unknown


def demo(ui_class):
    modules = [Gui('aaaa', [], {}, {}, '', False, False), Unknown('bbbb', [], {}, {}, '', False, False)]
    ui = ui_class(modules)
    res = ui.show()
    for r in res:
        print(r)
