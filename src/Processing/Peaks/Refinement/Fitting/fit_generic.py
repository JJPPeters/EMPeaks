import numpy as np
from scipy import ndimage
from lmfit import Model, Parameter

from Processing.Utilities import point_is_on_edge_of_image, get_image_region

# TODO: switch between initial esitmate of peaks or estimate as we fit?


def refine_fitting(data_in, points_float, initial_params, refine_func, fit_r, move_limit, frac_change, fit_method):
    if move_limit == 0:
        move_limit = np.inf

    if frac_change == 0:
        frac_change = np.inf

    points_out = np.zeros_like(points_float)

    # copy our data as we will be modifying it
    diff_image = np.copy(data_in)
    fit_image = np.zeros_like(diff_image)

    # create array of x and y coordinates for our fit region
    region_sz = (2 * fit_r + 1)
    # this comes in the form of (y, x)
    region_coords = np.mgrid[0:region_sz, 0:region_sz] - fit_r

    # make a list of valid coordinates (i.e. within the circle, not the square!
    radius = np.hypot(*region_coords)
    radius_valid = radius <= fit_r

    region_coords_y = region_coords[0, radius_valid].ravel()
    region_coords_x = region_coords[1, radius_valid].ravel()

    # Make a list of values in our extended_r
    # this is an area where the peak may have an affect, but we don't fit to all of this
    extended_r = 3 * fit_r
    extended_sz = (2 * extended_r + 1)
    extended_shape = (extended_sz, extended_sz)
    extended_coords = np.mgrid[0:extended_sz, 0:extended_sz] - extended_r

    #
    # Sort our peaks by intensity
    #

    # apply a media filter to remove noise
    med_im = ndimage.median_filter(diff_image, size=3)

    # get positions as integers
    points_int = np.round(points_float).astype(np.int)

    peak_intensity = med_im[points_int[:, 0], points_int[:, 1]]

    # sort and reverse (get get largest first)
    sorted_point_inds = np.argsort(peak_intensity)[::-1]

    fit_model = Model(refine_func)

    good_peaks = np.zeros(points_float.shape[0]).astype(np.bool)

    for i in sorted_point_inds:

        # get our current point in float and integer format
        # REMEMBER: coords are defined as [y, x]
        p = points_float[i, :]
        pi = points_int[i, :]

        # check points are not outside image (or within 'r' of the edge)
        if point_is_on_edge_of_image(diff_image, p, extended_r):
            continue

        # get the region defined by 'r' from the integer peak position
        # NOTE: I am not copying this data, so modifying it will modify the original
        refine_square = get_image_region(diff_image, p, fit_r)

        refine_region = refine_square[radius_valid].ravel()

        # get the initial parameters for this peak
        # these_params = estimate_gauss_parameter(refine_square, p, fit_r, move_limit)
        these_params = initial_params[i]

        fit_params = fit_model.make_params()

        for key, val in these_params.items():
            # set our limits
            if key in ['offset', 'theta'] or val[0] == 0:
                lo = val[1]
                hi = val[2]
            else:
                delta = np.abs(val[0]) * frac_change
                lo = np.max([val[0] - delta, val[1]])
                hi = np.min([val[0] + delta, val[2]])

            fit_params.add(name=key, value=val[0], min=lo, max=hi)

        pc_y = p[0]-pi[0]
        fit_params.add(name='yo', value=pc_y, min=pc_y - move_limit, max=pc_y + move_limit)

        pc_x = p[1] - pi[1]
        fit_params.add(name='xo', value=pc_x, min=pc_x - move_limit, max=pc_x + move_limit)

        fit_result = fit_model.fit(refine_region, fit_params, yx=(region_coords_y, region_coords_x), method=fit_method)

        result_params = fit_result.params
        result_params['offset'].set(value=0)

        points_out[i, 0] = result_params['yo'].value + points_int[i, 0]
        points_out[i, 1] = result_params['xo'].value + points_int[i, 1]
        good_peaks[i] = True

        model_eval = fit_model.eval(result_params, yx=extended_coords)
        fitted_gauss = model_eval.reshape(extended_shape)

        diff_im = get_image_region(diff_image, p, extended_r)
        diff_im -= fitted_gauss

        fit_im = get_image_region(fit_image, p, extended_r)
        fit_im += fitted_gauss

    return points_out[good_peaks], fit_image, diff_image
