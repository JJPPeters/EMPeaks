from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog
from Processing.Image import bin_image, unbin_image

import numpy as np
from scipy import ndimage


class BinModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Transform']
        self.name = 'Bin'
        self.order_priority = 0

    def run(self):
        if not self.main_window.image_requirements_met():
            return
        im = self.active_image_window.image_plot.image_data

        controls = []

        if im.ndim > 0:
            controls.append(["SpinInt", 0, "x binning", (1, im.shape[0], 1, 1)])
        if im.ndim > 1:
            controls.append(["SpinInt", 1, "y binning", (1, im.shape[0], 1, 1)])
        if im.ndim > 2:
            controls.append(["SpinInt", 2, "z binning", (1, im.shape[0], 1, 1)])

        if im.ndim > 3:
            for i in range(im.ndim-3):
                controls.append(["SpinInt", 3+i, "Dim " + str(i+3) + " binning", (1, im.shape[0], 1, 1)])

        filterdialog = ProcessSettingsDialog(master=self.main_window.last_active,
                                             name="Bin",  # TODO: add old name to this?
                                             inputs=controls)

        filterdialog.sigApplyFilter.connect(self.do_binning)
        filterdialog.exec_()

        filterdialog.sigApplyFilter.disconnect(self.do_binning)

    def do_binning(self, params):
        image = self.active_image_window.image_plot.image_data

        binned = bin_image(image, params)

        # self.create_or_update_image("Image", binned, keep_view=False)
        self.main_window.create_new_image("Binned " + self.main_window.last_active.name, binned)


class UnBinModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Transform']
        self.name = 'Un-bin'
        self.order_priority = 0

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        xbin = ["SpinInt", 0, "x binning", (1, 2**20, 1, 1)]
        ybin = ["SpinInt", 1, "y binning", (1, 2**20, 1, 1)]

        filterdialog = ProcessSettingsDialog(master=self.main_window.last_active,
                                             name="Un-bin",  # TODO: add old name to this?
                                             inputs=[xbin, ybin])

        filterdialog.sigApplyFilter.connect(self.do_unbinning)
        filterdialog.exec_()

        filterdialog.sigApplyFilter.disconnect(self.do_unbinning)

    def do_unbinning(self, params):
        image = self.active_image_window.image_plot.image_data
        x_bin = params["x binning"]
        y_bin = params["y binning"]

        binned = unbin_image(image, x_bin, y_bin)

        self.create_or_update_image("Image", binned, keep_view=False)