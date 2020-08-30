from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

import numpy as np
from scipy import ndimage


class GaussFilterModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Gauss'
        self.order_priority = 0

    def run(self):
        if self.main_window.last_active is None or not isinstance(self.main_window.last_active, ImageWindow):
            return

        # todo: is there any sensible way to get this to work for complex (or do I care?)
        if np.iscomplexobj(self.active_image_window.image_plot.image_data):
            return

        # create parameters for dialog
        sigma = ["SpinFloat", 0, "Sigma", (1, 20, 0.25, 2)]
        order = ["SpinInt", 1, "Order", (0, 3, 1, 0)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name='Gaussian filter',
            function=self.doGaussian,
            inputs=[sigma, order],
            show_preview=True, preserve_image=True)

        self.add_widget_to_image_window(filter_settings, 0, 2)

    def doGaussian(self, params):
        vals = params
        f = lambda i: ndimage.gaussian_filter(i, sigma=vals[0], order=vals[1])

        self.perform_on_image(f)

        self.set_console_message("Gaussian filtered")
