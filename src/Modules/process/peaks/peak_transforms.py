from GUI.Modules.menu_entry_module import MenuEntryModule
import numpy as np
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

base_path = ['Process', 'Peaks', 'Transform']


class PeakTranslate(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Translate'
        self.order_priority = 520

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        x_shift = ["SpinFloat", 0, "Shift x:", (-np.inf, np.inf, 0.1, 0)]
        y_shift = ["SpinFloat", 1, "Shift y:", (-np.inf, np.inf, 0.1, 0)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Shift peaks",
            function=self.do_peak_shift,
            inputs=[x_shift, y_shift],
            show_preview=True, show_apply=False, preserve_peaks=True)
        
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_peak_shift(self, params):
        tag = 'Peaks'
        peaks = self.active_image_window.plottables[tag].points.copy()

        peaks[:, 0] += params[1]
        peaks[:, 1] += params[0]

        self.create_or_update_scatter(tag, peaks)


class PeakRotate(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Rotate'
        self.order_priority = 521

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        angle = ["SpinFloat", 0, "Angle:", (0, 360, 0.1, 0)]
        direction = ["Combo", 1, "Direction:", ('CCW', 'CW'), 0]
        # reference = ["Combo", 2, "Reference:", ('Centre', 'Top-left', 'Left', 'Bottom-left', 'Bottom', 'Bottom-right', 'Right', 'Top-Right', 'Top'), 0]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Transpose peaks",
            function=self.do_peak_rotate,
            inputs=[angle, direction],
            show_preview=True, show_apply=False, preserve_peaks=True)
        
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_peak_rotate(self, params):
        tag = 'Peaks'
        peaks = self.active_image_window.plottables[tag].points.copy()

        a = np.deg2rad(params[0])
        if params[1] == 'CW':
            a *= -1

        rot = np.array([[np.cos(a), -np.sin(a)],
                        [np.sin(a), np.cos(a)]])

        mid_point = (np.min(peaks, axis=0) + np.max(peaks, axis=0)) / 2

        rot_peaks = rot.dot((peaks - mid_point).T).T + mid_point

        self.create_or_update_scatter(tag, rot_peaks)
        
        
class PeakTranspose(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Transpose'
        self.order_priority = 522

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Transpose peaks",
            function=self.do_peak_transpose,
            inputs=[],
            show_preview=True, show_apply=False, preserve_peaks=True)
        
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_peak_transpose(self, params):
        tag = 'Peaks'
        peaks = self.active_image_window.plottables[tag].points.copy()

        peaks = np.fliplr(peaks)

        self.create_or_update_scatter(tag, peaks)
       
        
class PeakFlip(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Flip'
        self.order_priority = 523

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        direction = ["Combo", 0, "Direction:", ('Vertical', 'Horizontal'), 0]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Flip peaks",
            function=self.do_peak_flip,
            inputs=[direction],
            show_preview=True, show_apply=False, preserve_peaks=True)
        
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_peak_flip(self, params):
        tag = 'Peaks'
        peaks = self.active_image_window.plottables[tag].points.copy()
        shp = self.main_window.last_active.intensities.shape

        if params[0] == 'Horizontal':
            peaks[:, 1] = shp[1] - peaks[:, 1]
        else:
            peaks[:, 0] = shp[0] - peaks[:, 0]

        self.create_or_update_scatter(tag, peaks)