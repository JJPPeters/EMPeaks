import numpy as np
from Processing.Utilities import normalise_copy
from Processing.Utilities import gaussian_2d_fitting
from .fit_it_generic import refine_fitting
from Processing.Peaks.Refinement.Fitting.utilities import estimate_peak_parameters
from Processing.Utilities import point_is_on_edge_of_image, get_image_region


def do_fitting_it_gauss(data, points, fit_r, contribute_r, iterations, lim=0, frac_change=0, do_init_fit=True, fit_method='leastsq'):
    image = normalise_copy(data)

    culled_points, initial_params = estimate_gauss_parameters(image, points, fit_r)

    func = gaussian_2d_fitting
    test = refine_fitting(image, culled_points, initial_params, func, fit_r, contribute_r, iterations, lim, frac_change, fit_method, do_initial_fit=do_init_fit)
    return test


def estimate_gauss_parameter(image_region, r):
    amplitude, sigma, offset = estimate_peak_parameters(image_region, r)

    param_dict = {}
    param_dict['amplitude'] = (amplitude, 0.0, np.inf)
    param_dict['sigma_x'] = (sigma, 0.00001, np.inf)
    param_dict['sigma_y'] = (sigma, 0.00001, np.inf)
    param_dict['theta'] = (0.0, -np.pi / 2, np.pi / 2)
    param_dict['offset'] = (offset, 0.0, 1.0)  # assumes image will be normaliased

    return param_dict


def estimate_gauss_parameters(full_image, points, r):
    param_list = []
    good_points = np.zeros(points.shape[0]).astype(np.bool)
    for i, point in enumerate(points):
        if point_is_on_edge_of_image(full_image, point, r):
            # param_list.append(None)
            continue

        image_region = get_image_region(full_image, point, r)
        param_list.append(estimate_gauss_parameter(image_region, r))
        good_points[i] = True

    return points[good_points], param_list