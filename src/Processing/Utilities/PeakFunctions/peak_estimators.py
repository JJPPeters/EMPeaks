import numpy as np
# from Processing.Utilities import point_is_on_edge_of_image, get_image_region
import Processing.Utilities as PU


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# General function to try and estimate the amplitude, sigma and background offset of an image
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def estimate_peak_parameters(refine_region, r):
    # we need to determine (for our fitting)
    # amplitude, sigma, offset

    # get a very simple estimate of the background
    offset = np.min(refine_region)

    # get the maximum
    # Note that I don't use the max in case this peak is 'on the side' of another peak
    amplitude = refine_region[r, r]

    # sigma is the hard part
    # try to find a HWHM by finding closest pixel that is below half maximum

    # calculate the distance of all pixels from our current point
    region_sz = (2 * r + 1)
    region_coords = np.mgrid[0:region_sz, 0:region_sz] - r
    distance = np.hypot(*region_coords).ravel()

    # sort by distance
    inds = distance.argsort()
    reg_sort = np.ravel(refine_region)[inds]
    # get lowest value with intensity lower than half max
    half_max = (amplitude - offset) / 2 + offset
    hwhm_ind = np.argmax(reg_sort < half_max)
    # get distance and convert to a standard deviation
    hwhm = distance[inds][hwhm_ind]

    sigma = hwhm * 2 / 2.35482
    if sigma == 0:
        sigma = 1

    return amplitude, sigma, offset


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Gauss
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def estimate_gauss_parameter(image_region, r, rotate=False):
    amplitude, sigma, offset = estimate_peak_parameters(image_region, r)

    param_dict = {}
    #
    param_dict['amplitude'] = (amplitude, 0.0, np.inf)
    param_dict['sigma'] = (sigma, 0.00001, np.inf)
    param_dict['offset'] = (offset, 0.0, 1.0)  # assumes image will be normaliased

    if rotate:
        param_dict['sigma_y'] = (sigma, 0.00001, np.inf)
        param_dict['theta'] = (0.0, -np.pi / 2, np.pi / 2)

    return param_dict


def estimate_gauss_parameters(full_image, points, r, rotate=False):
    param_list = []
    good_points = np.zeros(points.shape[0]).astype(np.bool)
    for i, point in enumerate(points):
        if PU.point_is_on_edge_of_image(full_image, point, r):
            # param_list.append(None)
            continue

        image_region = PU.get_image_region(full_image, point, r)
        param_list.append(estimate_gauss_parameter(image_region, r, rotate))
        good_points[i] = True

    return points[good_points], param_list


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Skewed Gauss
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def estimate_skewed_gauss_parameter(image_region, r):
    amplitude, sigma, offset = estimate_peak_parameters(image_region, r)

    param_dict = {}
    #
    param_dict['amplitude'] = (amplitude, 0.0, np.inf)
    param_dict['sigma_x'] = (sigma, 0.00001, np.inf)
    param_dict['theta'] = (0.0, -np.pi / 2, np.pi / 2)
    param_dict['offset'] = (offset, 0.0, 1.0)  # assumes image will be normaliased

    param_dict['sigma_y'] = (sigma, 0.00001, np.inf)

    param_dict['skew_x'] = (0.0, 0.0, np.inf)
    param_dict['skew_y'] = (0.0, 0.0, np.inf)

    return param_dict


def estimate_skewed_gauss_parameters(full_image, points, r):
    param_list = []
    good_points = np.zeros(points.shape[0]).astype(np.bool)
    for i, point in enumerate(points):
        if PU.point_is_on_edge_of_image(full_image, point, r):
            # param_list.append(None)
            continue

        image_region = PU.get_image_region(full_image, point, r)
        param_list.append(estimate_skewed_gauss_parameter(image_region, r))
        good_points[i] = True

    return points[good_points], param_list


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Lorentz
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def estimate_lorentz_parameter(image_region, r, rotate=False):
    amplitude, sigma, offset = estimate_peak_parameters(image_region, r)

    # convert sigma to HWHM
    sigma *= 2.35482 / 2

    param_dict = {}
    param_dict['amplitude'] = (amplitude, 0.0, np.inf)
    param_dict['gamma'] = (sigma, 0.00001, np.inf)
    param_dict['offset'] = (offset, 0.0, 1.0)  # assumes image will be normaliased

    if rotate:
        param_dict['gamma_y'] = (sigma, 0.00001, np.inf)
        param_dict['theta'] = (0.0, -np.pi / 2, np.pi / 2)

    return param_dict


def estimate_lorentz_parameters(full_image, points, r, rotate=False):
    param_list = []
    good_points = np.zeros(points.shape[0]).astype(np.bool)
    for i, point in enumerate(points):
        if PU.point_is_on_edge_of_image(full_image, point, r):
            # param_list.append(None)
            continue

        image_region = PU.get_image_region(full_image, point, r)
        param_list.append(estimate_lorentz_parameter(image_region, r, rotate))
        good_points[i] = True

    return points[good_points], param_list


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Pearson VII
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def estimate_pearson_parameter(image_region, r, rotate=False):
    amplitude, sigma, offset = estimate_peak_parameters(image_region, r)

    param_dict = {}
    param_dict['amplitude'] = (amplitude, 0.0, np.inf)
    param_dict['m'] = (5, 0.00001, np.inf)
    param_dict['w'] = (sigma, 0.00001, np.inf)
    param_dict['offset'] = (offset, 0.0, 1.0)  # assumes image will be normalised

    if rotate:
        param_dict['w_y'] = (sigma, 0.00001, np.inf)
        param_dict['theta'] = (0.0, -np.pi / 2, np.pi / 2)

    return param_dict


def estimate_pearson_parameters(full_image, points, r, rotate=False):
    param_list = []
    good_points = np.zeros(points.shape[0]).astype(np.bool)
    for i, point in enumerate(points):
        if PU.point_is_on_edge_of_image(full_image, point, r):
            # param_list.append(None)
            continue

        image_region = PU.get_image_region(full_image, point, r)
        param_list.append(estimate_pearson_parameter(image_region, r, rotate))
        good_points[i] = True

    return points[good_points], param_list


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Pseudo Voigt
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def estimate_voigt_parameter(image_region, r, rotate=False):
    amplitude, sigma, offset = estimate_peak_parameters(image_region, r)

    # gamma is hwhm
    gamma = 2.35482 / 2

    param_dict = {}
    param_dict['amplitude'] = (amplitude, 0.0, np.inf)
    param_dict['frac'] = (0.5, 0.0, 1.0)
    param_dict['sigma'] = (sigma, 0.00001, np.inf)
    param_dict['gamma'] = (gamma, 0.00001, np.inf)
    param_dict['offset'] = (offset, 0.0, 1.0)  # assumes image will be normaliased

    if rotate:
        param_dict['sigma_y'] = (sigma, 0.00001, np.inf)
        param_dict['gamma_y'] = (gamma, 0.00001, np.inf)
        param_dict['theta'] = (0.0, -np.pi / 2, np.pi / 2)

    return param_dict


def estimate_voigt_parameters(full_image, points, r, rotate=False):
    param_list = []
    good_points = np.zeros(points.shape[0]).astype(np.bool)
    for i, point in enumerate(points):
        if PU.point_is_on_edge_of_image(full_image, point, r):
            # param_list.append(None)
            continue

        image_region = PU.get_image_region(full_image, point, r)
        param_list.append(estimate_voigt_parameter(image_region, r, rotate))
        good_points[i] = True

    return points[good_points], param_list
