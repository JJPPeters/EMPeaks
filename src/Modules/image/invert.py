from GUI.Modules.menu_entry_module import MenuEntryModule

import numpy as np


class InvertModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image']
        self.name = 'Invert'
        self.order_priority = 0

    def invert(self, image):
        return image * -1

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        self.perform_on_image(self.invert)

        self.set_console_message("Image inverted")
