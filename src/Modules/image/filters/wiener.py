from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

import numpy as np
from scipy import signal


class WienerFilterModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Wiener'
        self.order_priority = 0

    def run(self):
        if self.main_window.last_active is None or not isinstance(self.main_window.last_active, ImageWindow):
            return

        # todo: is there any sensible way to get this to work for complex (or do I care?)
        if np.iscomplexobj(self.active_image_window.image_plot.image_data):
            return

        # create parameters for dialog
        size = ["SpinInt", 0, "Area:", (1, 19, 2, 5)]
        # noise = ["SpinFloat", 1, "Noise Power:", (0,5,0.25,1)]

        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            function=self.doWiener,
            name="Wiener",
            inputs=[size],
            show_preview=True, preserve_image=True)  # , noise])
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def doWiener(self, params):
        vals = params
        if vals[0] == 1:
            vals[0] = None  # Use value of 1 to let scipy estimate noise

        # , noise=vals[1]) )
        # self.main_window.last_active.setImage(signal.wiener(image, mysize=vals[0]), keep_view=True)
        f = lambda i: signal.wiener(i, mysize=vals[0])

        self.perform_on_image(f)
