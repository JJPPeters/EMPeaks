import numpy as np
from Processing.Utilities import normalise_copy
from Processing.Utilities.PeakFunctions import lorentz_2d_fitting
from .fit_it_generic import refine_fitting
from Processing.Utilities.PeakFunctions import estimate_lorentz_parameters


def do_fitting_it_lorentz(data, points, fit_r, contribute_r, iterations, lim=0, frac_change=0, do_init_fit=True, fit_method='leastsq', use_rot=False):
    image = normalise_copy(data)

    culled_points, initial_params = estimate_lorentz_parameters(image, points, fit_r, use_rot)

    func = lorentz_2d_fitting
    test = refine_fitting(image, culled_points, initial_params, func, fit_r, contribute_r, iterations, lim, frac_change, fit_method, do_initial_fit=do_init_fit)
    return test