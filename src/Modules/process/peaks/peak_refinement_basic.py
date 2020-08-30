from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI.Dialogs.process_settings_dialog import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame
import numpy as np
import time
from Processing.Peaks import do_interp, do_centroid, do_parabola, do_maximum
from GUI.Utilities.enums import Console
from GUI import ImageWindow

base_path = ['Process', 'Peaks', 'Refine']


class RefineCentroid(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Centroid'
        self.order_priority = 600

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        refine_radius = ["SpinInt", 0, "Radius", (1, 100, 1, 1)]
        shift_limit = ["SpinInt", 1, "Shift limit", (0, 100, 1, 0)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Centroid",
            function=lambda p: self.do_refine_centroid(p, tag),
            inputs=[refine_radius, shift_limit],
            show_preview=True, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_centroid(self, params, tag):
        image = self.active_image_window.image_plot.image_data
        peaks = self.active_image_window.plottables[tag].points

        start_time = time.time()
        new_points, stats = do_centroid(image, peaks, r=params["Radius"], lim=params["Shift limit"])

        self.create_or_update_scatter(tag, new_points)

        self.set_console_message("Refined peaks using centroids in %0.5fs (%d didn't refine, %d moved outside "
                                        "the limits and %d were removed from edges)" % (time.time() - start_time,
                                                                                        stats[1],
                                                                                        stats[0],
                                                                                        stats[2]))


class RefineMaximum(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Maximum'
        self.order_priority = 601

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        refine_radius = ["SpinInt", 0, "Radius", (1, 100, 1, 1)]
        shift_limit = ["SpinInt", 1, "Shift limit", (0, 100, 1, 0)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Maximum",
            function=lambda p: self.do_refine_maximum(p, tag),
            inputs=[refine_radius, shift_limit],
            show_preview=True, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_maximum(self, params, tag):
        image = self.active_image_window.image_plot.image_data
        peaks = self.active_image_window.plottables[tag].points

        start_time = time.time()
        new_points, stats = do_maximum(image, peaks, r=params["Radius"], lim=params["Shift limit"])
        self.create_or_update_scatter(tag, new_points)

        self.main_window.set_console_message("Refined peaks to nearest maximum in %0.5fs (%d didn't refine, %d moved outside"
                                        "the limits and %d were removed from edges)" % (time.time() - start_time,
                                                                                        stats[2],
                                                                                        stats[1],
                                                                                        stats[3]),
                                        Console.Message)
        

class RefineInterpolate(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Interpolate'
        self.order_priority = 602

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        refine_radius = ["SpinInt", 0, "Radius", (1, 100, 1, 1)]
        shift_limit = ["SpinInt", 1, "Shift limit", (0, 100, 1, 0)]
        pixel_divs = ["SpinInt", 2, "Pixel divisions", (2, 100, 1, 20)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Interpolate",
            function=lambda p: self.do_refine_interp(p, tag),
            inputs=[refine_radius, shift_limit, pixel_divs],
            show_preview=True, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_interp(self, params, tag):
        image = self.active_image_window.image_plot.image_data
        peaks = self.active_image_window.plottables[tag].points

        start_time = time.time()
        new_points, stats = do_interp(image, peaks,
                                      r=params["Radius"], lim=params["Shift limit"], zoom=params["Pixel divisions"])

        self.create_or_update_scatter(tag, new_points)

        self.main_window.set_console_message("Refined peaks using interpolation in %0.5fs (%d didn't "
                                        "refine, %d moved outside the limits and %d were removed from edges)"
                                        % (time.time() - start_time,
                                           stats[2],
                                           stats[1],
                                           stats[3]),
                                        Console.Message)


class RefineParabola(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Parabola'
        self.order_priority = 603

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        refine_radius = ["SpinInt", 0, "Radius", (1, 100, 1, 1)]
        shift_limit = ["SpinInt", 1, "Shift limit", (0, 100, 1, 0)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Parabola",
            function=lambda p: self.do_refine_parabola(p, tag),
            inputs=[refine_radius, shift_limit],
            show_preview=True, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_parabola(self, params, tag):
        image = self.active_image_window.image_plot.image_data
        peaks = self.active_image_window.plottables[tag].points
        v = params

        start_time = time.time()
        new_points, stats = do_parabola(image, peaks,
                                        r=v["Radius"], lim=v["Shift limit"])
        self.create_or_update_scatter(tag, new_points)

        self.main_window.set_console_message("Refined peaks using parabolae in %0.5fs (%d didn't "
                                        "refine, %d moved outside the limits and %d were removed from edges)"
                                        % (time.time() - start_time,
                                           stats[2],
                                           stats[1],
                                           stats[3]),
                                        Console.Message)