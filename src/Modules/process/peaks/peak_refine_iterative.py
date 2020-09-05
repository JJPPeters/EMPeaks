from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame
from Processing.Peaks.Refinement.Fitting.Iterative import do_fitting_it_gauss, do_fitting_it_lorentz, do_fitting_it_pearson, do_fitting_it_voigt

base_path = ['Process', 'Peaks', 'Refine', 'Iterative']

fit_methods = ['leastsq', 'nelder', 'lbfgsb', 'powell', 'cg', 'newton', 'cobyla', 'bfgsb', 'tnc', 'trust-ncg',
               'trust-exact', 'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'differential_evolution',
               'basinhopping', 'ampgo', 'shgo', 'dual_annealing', 'emcee']


class IterativeRefineGaussian(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Gauss'
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
        frac_change = ["SpinInt", 4, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 5, "Fit method", fit_methods, 0]
        init_fit = ["Check", 6, "Fit initial", False]
        use_rot = ["Check", 7, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Gaussian",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method, init_fit, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities.copy()
        v = params

        fit_out = do_fitting_it_gauss(image, self.active_image_window.plottables[tag].points,
                                      fit_r=v[0],
                                      contribute_r=v[1],
                                      iterations=v[2],
                                      lim=v[3],
                                      frac_change=v[4] / 100,
                                      do_init_fit=v[6],
                                      fit_method=v[5],
                                      use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])


class IterativeRefineLorentzian(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Lorentz'
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
        frac_change = ["SpinInt", 4, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 5, "Fit method", fit_methods, 0]
        init_fit = ["Check", 6, "Fit initial", False]
        use_rot = ["Check", 7, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Lorentzian",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method, init_fit, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities.copy()
        v = params

        fit_out = do_fitting_it_lorentz(image, self.active_image_window.plottables[tag].points,
                                        fit_r=v[0],
                                        contribute_r=v[1],
                                        iterations=v[2],
                                        lim=v[3],
                                        frac_change=v[4] / 100,
                                        do_init_fit=v[6],
                                        fit_method=v[5],
                                        use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])


class IterativeRefinePearson(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Pearson VII'
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
        frac_change = ["SpinInt", 4, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 5, "Fit method", fit_methods, 0]
        init_fit = ["Check", 6, "Fit initial", False]
        use_rot = ["Check", 7, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Pearson VII",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method, init_fit, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities.copy()
        v = params

        fit_out = do_fitting_it_pearson(image, self.active_image_window.plottables[tag].points,
                                        fit_r=v[0],
                                        contribute_r=v[1],
                                        iterations=v[2],
                                        lim=v[3],
                                        frac_change=v[4] / 100,
                                        do_init_fit=v[6],
                                        fit_method=v[5],
                                        use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])


class IterativeRefineVoigt(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Pseudo Voigt'
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
        frac_change = ["SpinInt", 4, "Parameter change percent", (0, max_int, 5, 0)]
        fit_method = ["Combo", 5, "Fit method", fit_methods, 0]
        init_fit = ["Check", 6, "Fit initial", False]
        use_rot = ["Check", 7, "θ symmetric", True]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.active_image_window,
            name="Pseudo Voigt",
            function=lambda p: self.do_refine_gaussian_iterative(p, tag),
            inputs=[refine_radius, contribution_radius, iterations, shift_limit, frac_change, fit_method, init_fit, use_rot],
            show_preview=False, show_apply=False, preserve_peaks=True)
        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_refine_gaussian_iterative(self, params, tag):
        image = self.active_image_window.image_plot.intensities.copy()
        v = params

        fit_out = do_fitting_it_voigt(image, self.active_image_window.plottables[tag].points,
                                      fit_r=v[0],
                                      contribute_r=v[1],
                                      iterations=v[2],
                                      lim=v[3],
                                      frac_change=v[4] / 100,
                                      do_init_fit=v[6],
                                      fit_method=v[5],
                                      use_rot=not v['θ symmetric'])

        self.create_or_update_scatter(tag, fit_out[0])

        self.main_window.create_new_image(self.main_window.last_active.name + ' fit', fit_out[2])
        self.main_window.create_new_image(self.main_window.last_active.name + ' fit difference', fit_out[1])
