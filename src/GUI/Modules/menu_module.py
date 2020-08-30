from GUI.Modules.module import Module
import numpy as np


class MenuModule(Module):
    menu_structure = []
    menu = None
    order_priority = float('inf')

    def __init__(self):
        super().__init__()
        #
        # self.menu_structure = []
        # self.menu = None
        #
        # self.actions = {}
        # self.sub_menus = {}

    def install(self):
        # Module.__init__(self)
        try:
            self.main_window
        except AttributeError:
            super().__init__()

        if self.main_window is not None:
            # attach self so not garbage collected
            self.main_window.modules.append(self)

            self.menu = self.main_window.ui.add_menu(self.menu_structure)

            return self.menu