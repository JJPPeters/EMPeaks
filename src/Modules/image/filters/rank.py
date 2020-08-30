from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

import numpy as np
from scipy import ndimage


class RankFilterModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Rank'
        self.order_priority = 0

    def run(self):
        if self.main_window.last_active is None or not isinstance(self.main_window.last_active, ImageWindow):
            return

        # todo: is there any sensible way to get this to work for complex (or do I care?)
        if np.iscomplexobj(self.active_image_window.image_plot.image_data):
            return

        # create parameters for dialog
        rank = ["SpinInt", 0, "Rank:", (-1, 20, 1, 0)]
        size = ["SpinInt", 1, "Size:", (1, 20, 1, 3)]
        mode = [
            "Combo", 2, "Mode:",
            ('reflect', 'constant', 'nearest', 'mirror', 'wrap'), 0]
        # only used in constant mode
        cval = ["SpinFloat", 3, "Constant:", (0, 20, 0.25, 0)]
        origin = ["SpinInt", 4, "Origin:", (0, 20, 1, 0)]

        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            function=self.doRank,
            name="Rank",
            inputs=[rank, size, mode, cval, origin],
            show_preview=True, preserve_image=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def doRank(self, params):
        vals = params
        # need some condition on rank and size
        f = lambda i: ndimage.rank_filter(i, rank=vals[0], size=vals[1], mode=vals[2], cval=vals[3], origin=vals[4])

        self.perform_on_image(f)