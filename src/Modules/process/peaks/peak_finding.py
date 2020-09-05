from GUI.Modules.menu_entry_module import MenuEntryModule
import numpy as np
from Processing.Peaks import detect_local_maxima, average_nearby_peaks
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame
from Processing.Utilities import normalise_in_place
from skimage.feature import blob_dog, blob_log, blob_doh

base_path = ['Process', 'Peaks']


class PeaksFindMaxima(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Find maxima'
        self.order_priority = 500

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        min_rad = ["SpinInt", 0, "Min radius", (1, 100, 1, 1)]
        max_intens = ["SpinFloat", 1, "Max intensity", (0, 1, 0.1, 0)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Maxima",
            function=self.do_find_pixel_maxima,
            inputs=[min_rad, max_intens],
            show_preview=True, show_apply=False, preserve_peaks=True)

        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_find_pixel_maxima(self, params):
        image = self.main_window.last_active.image_plot.intensities
        v = params

        peaks = detect_local_maxima(image, v[0], v[1])

        self.create_or_update_scatter('Peaks', peaks)

        self.set_console_message("Local maxima found")


class PeaksAddMaxima(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Add peaks'
        self.order_priority = 501

    def run(self):
        if not self.main_window.image_requirements_met():
            return
        self.main_window.last_active.click_add_point()


class PeaksAverageClusters(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Average clusters'
        self.order_priority = 502

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        min_rad = ["SpinInt", 0, "Min radius", (1, 100, 2, 1)]
        do_av = ["Check", 1, "Average", False]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Average clusters",
            function=self.do_find_pixel_maxima,
            inputs=[min_rad, do_av],
            show_preview=True, show_apply=False, preserve_peaks=True)

        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_find_pixel_maxima(self, params):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        peaks = self.main_window.last_active.plottables[tag].points
        image = self.main_window.last_active.image_plot.intensities

        new_peaks = average_nearby_peaks(image, peaks, r=params[0], use_average=params[1])

        self.create_or_update_scatter(tag, new_peaks)
        
        
class PeaksFindLog(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path + ['Blob detection']
        self.name = 'Laplacian of Gaussian'
        self.order_priority = 510

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        min_sigma = ["SpinFloat", 0, "Min sigma:", (1, 100, 0.5, 1)]
        max_sigma = ["SpinFloat", 1, "Max sigma:", (1, 1000, 0.5, 50)]
        num_sigma = ["SpinInt", 2, "Num. sigma:", (1, 100, 1, 10)]
        thresh = ["SpinFloat", 3, "Threshold:", (0.0, 1.0, 0.05, 0.2)]
        overlap = ["SpinFloat", 4, "Overlap:", (0.0, 1.0, 0.05, 0.5)]
        log_scale = ["Combo", 5, "Log scale:", ('Enabled', 'Disabled'), 1]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="LoG",
            function=self.do_l_of_g,
            inputs=[min_sigma, max_sigma, num_sigma, thresh, overlap, log_scale],
            show_preview=True, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_l_of_g(self, params):
        image = self.main_window.last_active.image_plot.intensities
        v = params
        temp = np.array(image, copy=True, order='C')
        normalise_in_place(temp)
        blobs = blob_log(temp, min_sigma=v[0], max_sigma=v[1], num_sigma=v[2], threshold=v[3], overlap=v[4],
                         log_scale=v[5] == 'Enabled')
        # third column is radius
        if blobs.size != 0:
            self.create_or_update_scatter('Peaks', blobs[:, :2])
        
        
class PeaksFindDog(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path + ['Blob detection']
        self.name = 'Difference of Gaussian'
        self.order_priority = 511

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        min_sigma = ["SpinFloat", 0, "Min sigma:", (1, 100, 0.5, 1)]
        max_sigma = ["SpinFloat", 1, "Max sigma:", (1, 1000, 0.5, 50)]
        ratio_sigma = ["SpinFloat", 2, "Sigma ratio:", (1, 100, 1, 10)]
        thresh = ["SpinFloat", 3, "Threshold:", (0.0, 1.0, 0.05, 0.2)]
        overlap = ["SpinFloat", 4, "Overlap:", (0.0, 1.0, 0.05, 0.5)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="DoG",
            function=self.do_d_of_g,
            inputs=[min_sigma, max_sigma, ratio_sigma, thresh, overlap],
            show_preview=True, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_d_of_g(self, params):
        image = self.main_window.last_active.image_plot.intensities
        v = params
        temp = np.array(image, copy=True, order='C')
        normalise_in_place(temp)
        blobs = blob_dog(temp, min_sigma=v[0], max_sigma=v[1], sigma_ratio=v[2], threshold=v[3], overlap=v[4])
        # third column is radius
        if blobs.size != 0:
            self.create_or_update_scatter('Peaks', blobs[:, :2])
        
        
class PeaksFindDoh(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path + ['Blob detection']
        self.name = 'Determinant of Hessian'
        self.order_priority = 512

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met() or not self.main_window.confirm_replace_peaks(tag):
            return

        min_sigma = ["SpinFloat", 0, "Min sigma:", (1, 100, 0.5, 1)]
        max_sigma = ["SpinFloat", 1, "Max sigma:", (1, 1000, 0.5, 50)]
        num_sigma = ["SpinInt", 2, "Num. sigma:", (1, 100, 1, 10)]
        thresh = ["SpinFloat", 3, "Threshold:", (0.0, 1.0, 0.05, 0.2)]
        overlap = ["SpinFloat", 4, "Overlap:", (0.0, 1.0, 0.05, 0.5)]
        log_scale = ["Combo", 5, "Log scale:", ('Enabled', 'Disabled'), 1]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="DoH",
            function=self.do_d_of_h,
            inputs=[min_sigma, max_sigma, num_sigma, thresh, overlap, log_scale],
            show_preview=True, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_d_of_h(self, params):
        image = self.main_window.last_active.image_plot.intensities
        v = params
        temp = np.array(image, copy=True, order='C')
        normalise_in_place(temp)
        blobs = blob_doh(temp, min_sigma=v[0], max_sigma=v[1], num_sigma=v[2], threshold=v[3], overlap=v[4],
                         log_scale=v[5] == 'Enabled')
        # third column is radius
        if blobs.size != 0:
            self.create_or_update_scatter('Peaks', blobs[:, :2])