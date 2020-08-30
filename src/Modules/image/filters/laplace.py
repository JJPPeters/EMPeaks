from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

import numpy as np
from scipy import ndimage


class LapalceFilterModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Laplace'
        self.order_priority = 0

    def run(self):
        if self.main_window.last_active is None or not isinstance(self.main_window.last_active, ImageWindow):
            return

        # todo: is there any sensible way to get this to work for complex (or do I care?)
        if np.iscomplexobj(self.active_image_window.image_plot.image_data):
            return

        # create parameters for dialog
        mode = [
            "Combo", 0, "Mode:",
            ('reflect', 'constant', 'nearest', 'mirror', 'wrap'), 0]
        # only used in constant mode
        cval = ["SpinFloat", 1, "Constant:", (0, 20, 0.25, 0)]

        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            function=self.doLaplace,
            name="Laplace",
            inputs=[mode, cval],
            show_preview=True, preserve_image=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def doLaplace(self, params):
        vals = params
        f = lambda i: ndimage.laplace(i, mode=vals[0], cval=vals[1])

        self.perform_on_image(f)
