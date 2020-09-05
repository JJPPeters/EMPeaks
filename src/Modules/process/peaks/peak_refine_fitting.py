from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame
from Processing.Peaks.Refinement.Fitting import do_fitting_gauss, do_fitting_lorentz, do_fitting_pearson, do_fitting_voigt

base_path2 = ['Process', 'Peaks', 'Refine', 'Fitting']

fit_methods = ['leastsq', 'nelder', 'lbfgsb', 'powell', 'cg', 'newton', 'cobyla', 'bfgsb', 'tnc', 'trust-ncg',
               'trust-exact', 'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'differential_evolution',
               'basinhopping', 'ampgo', 'shgo', 'dual_annealing', 'emcee']


class RefineGaussianFit(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path2
        self.name = 'Gauss'
        self.order_priority = 610

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        shift_limit = ["SpinFloat", 1, "Shift limit", (0, max_int, 1, 1)]
        frac_change = ["SpinInt", 2, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 3, "Fit method", fit_methods, 0]
        use_rot = ["Check", 4, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Gaussian fit",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, shift_limit, frac_change, fit_method, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        fit_out = do_fitting_gauss(image, self.active_image_window.plottables[tag].points,
                                   fit_r=v["Fit radius"],
                                   lim=v["Shift limit"],
                                   frac_change=v['Parameter change percent'],
                                   fit_method=v["Fit method"],
                                   use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])


class RefineLorentzFit(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path2
        self.name = 'Lorentz'
        self.order_priority = 610

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        shift_limit = ["SpinFloat", 1, "Shift limit", (0, max_int, 1, 1)]
        frac_change = ["SpinInt", 2, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 3, "Fit method", fit_methods, 0]
        use_rot = ["Check", 4, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Lorentz",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, shift_limit, frac_change, fit_method, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        fit_out = do_fitting_lorentz(image, self.active_image_window.plottables[tag].points,
                                     fit_r=v["Fit radius"],
                                     lim=v["Shift limit"],
                                     frac_change=v['Parameter change percent'],
                                     fit_method=v["Fit method"],
                                     use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])


class RefinePearsonFit(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path2
        self.name = 'Pearson VII'
        self.order_priority = 610

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        shift_limit = ["SpinFloat", 1, "Shift limit", (0, max_int, 1, 1)]
        frac_change = ["SpinInt", 2, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 3, "Fit method", fit_methods, 0]
        use_rot = ["Check", 4, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Pearson",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, shift_limit, frac_change, fit_method, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        fit_out = do_fitting_pearson(image, self.active_image_window.plottables[tag].points,
                                     fit_r=v["Fit radius"],
                                     lim=v["Shift limit"],
                                     frac_change=v['Parameter change percent'],
                                     fit_method=v["Fit method"],
                                     use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])


class RefineVoigtFit(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path2
        self.name = 'Pseudo Voigt'
        self.order_priority = 610

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        # this seems like a shit way of doing this
        max_int = 2 ** 32 / 2 - 1

        refine_radius = ["SpinInt", 0, "Fit radius", (1, max_int, 1, 10)]
        shift_limit = ["SpinFloat", 1, "Shift limit", (0, max_int, 1, 1)]
        frac_change = ["SpinInt", 2, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 3, "Fit method", fit_methods, 0]
        use_rot = ["Check", 4, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Voigt",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, shift_limit, frac_change, fit_method, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities
        v = params

        fit_out = do_fitting_voigt(image, self.active_image_window.plottables[tag].points,
                                   fit_r=v["Fit radius"],
                                   lim=v["Shift limit"],
                                   frac_change=v['Parameter change percent'],
                                   fit_method=v["Fit method"],
                                   use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])
