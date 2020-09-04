import numpy as np
from Processing.Utilities import normalise_copy
from Processing.Utilities import lorentz_2d_fitting
from .fit_generic import refine_fitting
from Processing.Peaks.Refinement.Fitting.utilities import estimate_peak_parameters
from Processing.Utilities import point_is_on_edge_of_image, get_image_region


def do_fitting_lorentz(data, points, fit_r=10, lim=1, frac_change=0, fit_method='leastsq'):
    image = normalise_copy(data)

    initial_params = estimate_lorentz_parameters(image, points, fit_r)

    func = lorentz_2d_fitting
    test = refine_fitting(image, points, initial_params, func, fit_r, lim, frac_change, fit_method)
    return test


def estimate_lorentz_parameter(image_region, point, r):
    amplitude, sigma, offset = estimate_peak_parameters(image_region, r)

    param_dict = {}
    param_dict['amplitude'] = (amplitude, 0.0, np.inf)
    param_dict['gamma_x'] = (sigma, 0.00001, np.inf)
    param_dict['gamma_y'] = (sigma, 0.00001, np.inf)
    param_dict['theta'] = (0.0, -np.pi / 2, np.pi / 2)
    param_dict['offset'] = (offset, 0.0, 1.0)  # assumes image will be normaliased

    return param_dict


def estimate_lorentz_parameters(full_image, points, r):
    param_list = []
    for point in points:
        if point_is_on_edge_of_image(full_image, point, r):
            param_list.append(None)
            continue

        image_region = get_image_region(full_image, point, r)
        param_list.append(estimate_lorentz_parameter(image_region, point, r))

    return param_list