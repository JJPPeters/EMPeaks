from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

import numpy as np
from scipy import ndimage


class SobelFilterModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Sobel'
        self.order_priority = 0

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        # todo: is there any sensible way to get this to work for complex (or do I care?)
        if np.iscomplexobj(self.active_image_display.image_plot.image_data):
            return

        # create parameters for dialog
        axis = ["SpinInt", 0, "Axis:", (0, 1, 1, -1)]
        mode = [
            "Combo", 1, "Mode:",
            ('reflect', 'constant', 'nearest', 'mirror', 'wrap'), 0]
        # only used in constant mode
        cval = ["SpinFloat", 2, "Constant:", (0, 20, 0.25, 0)]

        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            function=self.doSobel,
            name="Sobel",
            inputs=[axis, mode, cval],
            show_preview=True, preserve_image=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def doSobel(self, params):
        vals = params
        f = lambda i: ndimage.sobel(i, axis=vals[0], mode=vals[1], cval=vals[2])

        self.perform_on_image(f)
