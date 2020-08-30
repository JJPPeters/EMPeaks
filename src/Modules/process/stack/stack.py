from GUI.Modules.menu_entry_module import MenuEntryModule
from Processing.Utilities.arrays import average_nth_elements
from GUI.Dialogs.process_settings_dialog import ProcessSettingsDialog
from Processing.Registration import rigid_align, overdetermined_rigid_align, pyramid_rigid_align
import numpy as np


class StackSum(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Process', 'Stack']
        self.name = 'Sum stack'
        self.order_priority = 101

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        im = self.active_image_window.image_plot.image_data

        if im.ndim != 3:
            return

        sum_im = np.sum(im, axis=2)

        self.main_window.create_new_image("Summed " + self.main_window.last_active.name, sum_im)
