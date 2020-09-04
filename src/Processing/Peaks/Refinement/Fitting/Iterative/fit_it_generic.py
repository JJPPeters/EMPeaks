import numpy as np
from scipy import ndimage
from lmfit import Model

from Processing.Utilities import point_is_on_edge_of_image, get_image_region


########################################################################################################################
# refine_fitting
########################################################################################################################
# Inputs
#
# data - the image the points are to be refined using
# float_points - list of positions as floats, each row being [y, s]
# refine_func - function takes y, x coords, some parameters and returns an image
# r - 'radius' to using from peak for refining (uses square, not circle)
# lim - limit of movement after refinement
# refine_args/kwargs - arguments used for fitting
########################################################################################################################
def refine_fitting(data_in, points_float, initial_params, refine_func,
                   fit_r, contribute_r, iterations, move_limit, frac_change, fit_method, do_initial_fit=False):

    if move_limit == 0:
        move_limit = np.inf

    if frac_change == 0:
        frac_change = np.inf

    points_out = np.copy(points_float)

    point_params = initial_params.copy()

    # this is to stop peaks wandering too far over multiple refinements
    # points_original = np.copy(points_float)

    # copy our data as we will be modifying it
    data = np.copy(data_in)

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
    # extended_r = 3 * fit_r
    extended_r = contribute_r
    extended_sz = (2 * extended_r + 1)
    extended_shape = (extended_sz, extended_sz)
    extended_coords = np.mgrid[0:extended_sz, 0:extended_sz] - extended_r

    #
    # Sort our peaks by intensity
    #

    # apply a media filter to remove noise
    med_im = ndimage.median_filter(data, size=3)

    # get positions as integers
    points_int = np.round(points_out).astype(np.int)

    peak_intensity = med_im[points_int[:, 0], points_int[:, 1]]

    # sort and reverse (get get largest first)
    sorted_point_inds = np.argsort(peak_intensity)[::-1]

    fit_model = Model(refine_func)

    good_peaks = np.zeros(points_float.shape[0]).astype(np.bool)

    # pre_test = np.zeros((region_sz, region_sz, sorted_point_inds.size))
    # out_test = np.zeros((region_sz, region_sz, sorted_point_inds.size))

    for ii in range(iterations):
        it_data = np.copy(data)

        # loop through our points to refine
        for i in sorted_point_inds:

            # REMEMBER: coords are defined as [y, x]
            p = points_out[i, :]
            pi = np.round(p).astype(np.int)

            # check points are not outside image (or within 'r' of the edge)
            if point_is_on_edge_of_image(it_data, p, extended_r):
                continue

            # get the region defined by 'r' from the integer peak position
            # NOTE: I am not copying this data, so modifying it will modify the original
            ref_sq = get_image_region(it_data, p, fit_r)

            # this modifies the ref_sq, so make sure we use a copy of it
            if ii != 0 or not do_initial_fit:

                ref_sq = np.copy(ref_sq)

                # get all the peaks surrounding this
                i_in_region = (points_out[:, 1] >= (pi[1] - contribute_r)) & (points_out[:, 1] <= (pi[1] + contribute_r)) & \
                              (points_out[:, 0] >= (pi[0] - contribute_r)) & (points_out[:, 0] <= (pi[0] + contribute_r))
                i_in_region = np.where(i_in_region)[0]

                i_in_region = i_in_region[i_in_region != i]

                # get the floating point positions of our positions within the region
                points_in_region = points_out[i_in_region, :]
                # and get our fit parameters for these peaks
                params_in_region = []
                for id in i_in_region:
                    if id != i:
                        params_in_region.append(point_params[id])

                fit_params = []

                # I don't need to set all of these with min and max, I'm just using this as
                # an 'easy' way to plot the function
                for pt_r, prm in zip(points_in_region, params_in_region):
                    fp = fit_model.make_params()
                    for key, val in prm.items():
                        fp.add(name=key, value=val[0])

                    pc_y = pt_r[0] - pi[0]
                    fp.add(name='yo', value=pc_y)

                    pc_x = pt_r[1] - pi[1]
                    fp.add(name='xo', value=pc_x)

                    fp['offset'].set(value=0)

                    fit_params.append(fp)

                # now we need to subtract the peaks we aren't going to refine

                # pre_test[:, :, i] = np.copy(ref_sq)

                # now remove all the extra peaks we have
                for prm in fit_params:
                    ref_sq -= fit_model.eval(prm, yx=region_coords).reshape(ref_sq.shape)

                # out_test[:, :, i] = np.copy(ref_sq)

            # now apply the circle mask

            refine_region = ref_sq[radius_valid].ravel()

            # now we 'should' only have our peak left that we want to fit
            # so lets do that

            this_param = fit_model.make_params()

            for key, val in point_params[i].items():
                # set our limits
                if key in ['offset', 'theta'] or val[0] == 0:
                    lo = val[1]
                    hi = val[2]
                else:
                    delta = np.abs(val[0]) * frac_change
                    lo = np.max([val[0] - delta, val[1]])
                    hi = np.min([val[0] + delta, val[2]])

                this_param.add(name=key, value=val[0], min=lo, max=hi)

            pc_y = p[0] - pi[0]
            this_param.add(name='yo', value=pc_y, min=pc_y - move_limit, max=pc_y + move_limit)

            pc_x = p[1] - pi[1]
            this_param.add(name='xo', value=pc_x, min=pc_x - move_limit, max=pc_x + move_limit)

            fit_result = fit_model.fit(refine_region, this_param, yx=(region_coords_y, region_coords_x),
                                       method=fit_method)

            result_params = fit_result.params
            result_params['offset'].set(value=0)

            if ii == 0 and do_initial_fit:
                model_eval = fit_model.eval(result_params, yx=extended_coords)
                fitted_gauss = model_eval.reshape(extended_shape)

                diff_im = get_image_region(it_data, p, extended_r)
                diff_im -= fitted_gauss

            points_out[i, 0] = result_params['yo'].value + pi[0]
            points_out[i, 1] = result_params['xo'].value + pi[1]
            good_peaks[i] = True

            out_dict = {}
            for prm in result_params.values():
                out_dict[prm.name] = (prm.value, prm.min, prm.max)
            point_params[i] = out_dict

    fit_image = np.zeros_like(data)
    diff_image = data.copy()

    # create our reconstructed images here!
    for p, prm, gp in zip(points_out, point_params, good_peaks):
        if not gp:
            continue

        if point_is_on_edge_of_image(diff_image, p, extended_r):
            continue

        pi = np.round(p).astype(np.int)

        this_param = fit_model.make_params()

        for key, val in prm.items():
            this_param.add(name=key, value=val[0])

        pc_y = p[0] - pi[0]
        this_param.add(name='yo', value=pc_y)

        pc_x = p[1] - pi[1]
        this_param.add(name='xo', value=pc_x)

        this_param['offset'].set(value=0)

        model_eval = fit_model.eval(this_param, yx=extended_coords)
        fitted_gauss = model_eval.reshape(extended_shape)

        diff_im = get_image_region(diff_image, p, extended_r)
        diff_im -= fitted_gauss

        fit_im = get_image_region(fit_image, p, extended_r)
        fit_im += fitted_gauss

    return points_out[good_peaks], fit_image, diff_image  # , out_test, pre_test
