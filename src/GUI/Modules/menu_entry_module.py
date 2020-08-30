from PyQt5 import QtGui, QtCore, QtWidgets
# from GUI.Modules import MenuModule
from GUI.Modules.menu_module import MenuModule


class MenuEntryModule(MenuModule):
    # action = None
    # menu_structure = []
    name = ''
    shortcut = None

    def __init__(self):
        super().__init__()

        self.action = None

        # self.action = None
        # self.name = ''
        # self.order_priority = float('inf')
        # self.shortcut = None

    def install(self):
        if self.name == '':
            raise Warning('Must define module name')

        try:
            self.main_window
        except AttributeError:
            super().__init__()

        if self.main_window is not None:

            parent = super().install()

            menu_text = [m.text() for m in parent.actions()]
            if self.name in menu_text:
                raise Exception("Trying to load module under already used menu entry: " + self.name)

            if self.shortcut is not None:
                self.action = QtWidgets.QAction(parent)
                self.action.setShortcut(self.shortcut)

            else:
                self.action = QtWidgets.QAction(parent)

            self.action.setText(self.name)

            parent.addAction(self.action)
            self.action.triggered.connect(self.run)

    def run(self):
        raise Warning("MenuModule is designed to be overidden, cannot run bare module")
