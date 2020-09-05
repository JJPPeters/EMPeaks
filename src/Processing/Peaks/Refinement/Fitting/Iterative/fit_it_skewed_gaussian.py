import numpy as np
from Processing.Utilities import normalise_copy
from Processing.Utilities.PeakFunctions import skewed_gaussian_2d_fitting
from .fit_it_generic import refine_fitting
from Processing.Utilities.PeakFunctions import estimate_gauss_parameters


def do_fitting_it_gauss(data, points, fit_r, contribute_r, iterations, lim=0, frac_change=0, do_init_fit=True, fit_method='leastsq'):
    image = normalise_copy(data)

    culled_points, initial_params = estimate_skewed_gauss_parameters(image, points, fit_r)

    func = skewed_gaussian_2d_fitting
    test = refine_fitting(image, culled_points, initial_params, func, fit_r, contribute_r, iterations, lim, frac_change, fit_method, do_initial_fit=do_init_fit)
    return test