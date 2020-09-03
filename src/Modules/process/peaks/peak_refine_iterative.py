from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame
from Processing.Peaks import do_fitting_pearson_vii, do_fitting_gauss, do_fitting_voigt, do_fitting_lorentz
from GUI import ImageWindow

base_path = ['Process', 'Peaks', 'Refine']


class RefineGaussian(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Gaussian'
        self.order_priority = 610

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        contribution_radius = ["SpinInt", 1, "Contribution radius", (1, max_int, 1, 20)]
        iterations = ["SpinInt", 2, "Iterations", (1, max_int, 1, 2)]
        shift_limit = ["SpinFloat", 3, "Shift limit", (1, max_int, 1, 1)]
        frac_change = ["SpinInt", 4, "Parameter change percent", (1, max_int, 1, 30)]
        fit_method = ["Combo", 5, "Fit method", ('trf', 'dogbox'), 0]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Gaussian",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        new_points = do_fitting_gauss(image, self.active_image_window.plottables[tag].points,
                                      fit_r=v[0],
                                      contribute_r=v[1],
                                      iterations=v[2],
                                      lim=v[3],
                                      frac_change=v[4] / 100,
                                      fit_method=v[5])

        self.create_or_update_scatter(tag, new_points)
  
                
class RefineLorentzian(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Lorentzian'
        self.order_priority = 611

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        contribution_radius = ["SpinInt", 1, "Contribution radius", (1, max_int, 1, 20)]
        iterations = ["SpinInt", 2, "Iterations", (1, max_int, 1, 2)]
        shift_limit = ["SpinFloat", 3, "Shift limit", (1, max_int, 1, 1)]
        frac_change = ["SpinInt", 4, "Parameter change percent", (1, max_int, 1, 30)]
        fit_method = ["Combo", 5, "Fit method", ('trf', 'dogbox'), 0]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Gaussian",
            function=lambda p: self.do_refine_lorentzian_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_lorentzian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        new_points = do_fitting_lorentz(image, self.active_image_window.plottables[tag].points,
                                        fit_r=v[0],
                                        contribute_r=v[1],
                                        iterations=v[2],
                                        lim=v[3],
                                        frac_change=v[4] / 100,
                                        fit_method=v[5])

        self.create_or_update_scatter(tag, new_points)
        
        
class RefinePearsonVii(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Pearson VII'
        self.order_priority = 612

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        contribution_radius = ["SpinInt", 1, "Contribution radius", (1, max_int, 1, 20)]
        iterations = ["SpinInt", 2, "Iterations", (1, max_int, 1, 2)]
        shift_limit = ["SpinFloat", 3, "Shift limit", (1, max_int, 1, 1)]
        frac_change = ["SpinInt", 4, "Parameter change percent", (1, max_int, 1, 30)]
        fit_method = ["Combo", 5, "Fit method", ('trf', 'dogbox'), 0]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Pearson VII",
            function=lambda p: self.do_refine_pearsonvii_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method],
            show_preview=False, show_apply=False, preserve_peaks=True)

        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_pearsonvii_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        new_points = do_fitting_pearson_vii(image, self.active_image_window.plottables[tag].points,
                                            fit_r=v[0],
                                            contribute_r=v[1],
                                            iterations=v[2],
                                            lim=v[3],
                                            frac_change=v[4] / 100,
                                            fit_method=v[5])

        self.create_or_update_scatter(tag, new_points)
        
        
class RefineVoigt(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Voigt'
        self.order_priority = 613

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        contribution_radius = ["SpinInt", 1, "Contribution radius", (1, max_int, 1, 20)]
        iterations = ["SpinInt", 2, "Iterations", (1, max_int, 1, 2)]
        shift_limit = ["SpinFloat", 3, "Shift limit", (1, max_int, 1, 1)]
        frac_change = ["SpinInt", 4, "Parameter change percent", (1, max_int, 1, 30)]
        fit_method = ["Combo", 5, "Fit method", ('trf', 'dogbox'), 0]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Pearson VII iterative",
            function=lambda p: self.do_refine_pseudo_voigt_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method],
            show_preview=False, show_apply=False, preserve_image=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_pseudo_voigt_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        new_points = do_fitting_voigt(image, self.active_image_window.plottables[tag].points,
                                      fit_r=v[0],
                                      contribute_r=v[1],
                                      iterations=v[2],
                                      lim=v[3],
                                      frac_change=v[4] / 100,
                                      fit_method=v[5])

        self.create_or_update_scatter(tag, new_points)