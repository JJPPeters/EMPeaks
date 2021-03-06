from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

import numpy as np
from scipy import ndimage


class MedianFilterModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Median'
        self.order_priority = 0

    def run(self):
        if self.main_window.last_active is None or not isinstance(self.main_window.last_active, ImageWindow):
            return

        # todo: is there any sensible way to get this to work for complex (or do I care?)
        if np.iscomplexobj(self.active_image_window.image_plot.image_data):
            return

        # create parameters for dialog
        size = ["SpinInt", 0, "Size:", (1, 20, 1, 3)]
        mode = ["Combo", 1, "Mode:", ('reflect', 'constant', 'nearest', 'mirror', 'wrap'), 0]
        # only used in constant mode
        cval = ["SpinFloat", 2, "Constant:", (0, 20, 0.25, 0)]
        origin = ["SpinInt", 3, "Origin:", (0, 20, 1, 0)]

        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            function=self.doMedian,
            name="Median",
            inputs=[size, mode, cval, origin],
            show_preview=True, preserve_image=True)

        self.add_widget_to_image_window(filter_settings, 0, 2)

    def doMedian(self, params):
        vals = params
        if vals[3] >= vals[0]:
            vals[3] = vals[0] - 0.25

        f = lambda i: ndimage.median_filter(i, size=vals[0], mode=vals[1], cval=vals[2], origin=vals[3])

        self.perform_on_image(f)
