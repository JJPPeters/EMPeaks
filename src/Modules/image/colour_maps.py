from PyQt5 import QtCore, QtWidgets
from GUI.Modules.menu_module import MenuModule

import numpy as np


class ColourMapModule(MenuModule, QtCore.QObject):
    def __init__(self):
        MenuModule.__init__(self)
        QtCore.QObject.__init__(self)

        self.menu_structure = ['Image', 'Colour maps']

        self.order_priority = 999

        self.sub_menus = {}
        self.actions = {}

    def add_menu(self, text, enabled=True):
        if self.menu is None:
            raise Exception("Must install MenuModule before adding to it")

        sub_menu = QtWidgets.QMenu(self.menu)
        sub_menu.setTitle(text)
        sub_menu.setEnabled(enabled)

        self.menu.addAction(sub_menu.menuAction())

        self.sub_menus[text] = sub_menu

    def add_action(self, text, menu=None, enabled=True):
        if self.menu is None:
            raise Exception("Must install MenuModule before adding to it")

        parent_menu = self.menu
        if menu is not None and menu not in self.sub_menus:
            raise Exception("Trying to install action to menu that does not exist")
        elif menu is not None:
            parent_menu = self.sub_menus[menu]

        action = QtWidgets.QAction(parent_menu)
        action.setText(text)
        action.setEnabled(enabled)
        action.triggered.connect(self.run)

        parent_menu.addAction(action)
        self.actions[text] = action

    def install(self):
        super().install()

        col_maps = self.main_window.colour_maps

        keylist = sorted(col_maps, key=col_maps.get)

        for k in keylist:
            if col_maps[k][0] != "" and col_maps[k][0] not in self.sub_menus:
                self.add_menu(col_maps[k][0])

        for k in keylist:
            if col_maps[k][0] == "":
                self.add_action(k)
            else:
                self.add_action(k, menu=col_maps[k][0])

    def run(self):
        key = self.sender().text()
        if self.main_window.image_requirements_met():
            self.set_colour_map(key)
