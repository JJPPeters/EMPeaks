from PyQt5 import QtGui, QtWidgets


class ActionEntry(QtWidgets.QAction):
    def __init__(self, text="", action=None, enabled=True, shortcut=None, parent=None):
        super(ActionEntry, self).__init__(parent)

        self.setText(text)
        if action is not None:
            self.triggered.connect(action)

        self.setEnabled(enabled)

        if shortcut is not None:
            self.setShortcut(shortcut)

        if isinstance(parent, QtWidgets.QMenu) or issubclass(type(parent), QtWidgets.QMenu):
            parent.addAction(self)


class MenuEntry(QtWidgets.QMenu):
    def __init__(self, text="", enabled=True, parent=None):
        super(MenuEntry, self).__init__(parent)

        self.setTitle(text)

        # self.actions = []
        # self.menus = []

        self.setEnabled(enabled)

        if isinstance(parent, QtWidgets.QMenu) or issubclass(type(parent), QtWidgets.QMenu):
            parent.addMenu(self)

    def addAction(self, action):
        # if action not in self.actions:
        #     self.actions.append(action)
        super(MenuEntry, self).addAction(action)

    def addMenu(self, menu):
        # if menu not in self.menus:
        #     self.menus.append(menu)
        self.addAction(menu.menuAction())

    def createAction(self, text="", action=None, enabled=True, shortcut=None):
        action = ActionEntry(text, action, enabled, shortcut, self)
        self.addAction(action)
        return action

    def createMenu(self, text="", enabled=True):
        menu = MenuEntry(text, enabled, self)
        self.addMenu(menu)
        return menu