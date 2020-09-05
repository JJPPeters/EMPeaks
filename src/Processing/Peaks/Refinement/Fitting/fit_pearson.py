import numpy as np
from Processing.Utilities import normalise_copy
from Processing.Utilities.PeakFunctions import pearson_vii_2d_fitting
from .fit_generic import refine_fitting
from Processing.Utilities.PeakFunctions import estimate_pearson_parameters


def do_fitting_pearson(data, points, fit_r=10, lim=1, frac_change=0, fit_method='leastsq', use_rot=False):
    image = normalise_copy(data)

    culled_points, initial_params = estimate_pearson_parameters(image, points, fit_r, use_rot)

    func = pearson_vii_2d_fitting
    test = refine_fitting(image, culled_points, initial_params, func, fit_r, lim, frac_change, fit_method)
    return test
