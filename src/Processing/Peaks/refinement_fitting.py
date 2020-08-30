import numpy as np
from scipy.optimize import curve_fit
from enum import Enum

from Processing.Utilities import gaussian_2d, lorentz_2d, pearson_vii_2d, pseudo_voigt_2d
from Processing.Utilities import normalise_copy


class PeakType(Enum):
    Gaussian = 0
    Lorentzian = 1
    PearsonVII = 2
    PseudoVoigt = 3


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
def refine_fitting(data, points_float, fit_params, refine_func,
                   fit_r, contribute_r, iterations, move_limit, frac_change, fit_method, peak_type):

    # these are my checks that the inputs are at least vaguely sensible
    if points_float.shape[1] != 2 or points_float.shape[0] != fit_params.shape[0]:
        raise Exception("Iterative refine function generic has unusable inputs (incompatible shapes)")

    # this is to stop peaks wandering too far over multiple refinements
    points_original = np.copy(points_float)

    # get the dimensions of the input image
    im_dim = data.shape

    # get the number of points for convenience
    num_points = points_float.shape[0]

    # create array of x and y coordinates
    region_sz = (2 * fit_r + 1)
    # this comes in the form of (y, x)
    region_coords = np.mgrid[0:region_sz, 0:region_sz]

    ftol = 1e-8
    xtol = 1e-8
    gtol = 1e-8

    for ii in range(iterations):
        # loop through our points to refine
        for i in range(num_points):
            # print("Refining peak: " + str(i) + " of " + str(num_points) + " (" + str(100 * i / num_points) + "%)")
            # get our point in integer format
            # REMEMBER: coords are defined as [y, x]
            p_int = np.round(points_float[i, :]).astype(np.int)

            # check points are not outside image (or within 'r' of the edge)
            if (im_dim[1] - fit_r) <= p_int[1] or p_int[1] < fit_r or (im_dim[0] - fit_r) <= p_int[0] or p_int[0] < fit_r:
                continue

            # get the region defined by 'r' from the integer peak position
            refine_region = np.copy(data[(p_int[0] - fit_r):(p_int[0] + fit_r + 1), (p_int[1] - fit_r):(p_int[1] + fit_r + 1)])

            # if normalise:
            #     refine_region = normalise_copy(refine_region)

            # get all the peaks surrounding this
            i_in_region = (points_float[:, 1] >= (p_int[1] - contribute_r)) & (points_float[:, 1] <= (p_int[1] + contribute_r)) & \
                          (points_float[:, 0] >= (p_int[0] - contribute_r)) & (points_float[:, 0] <= (p_int[0] + contribute_r))

            # get the floating point positions of our positions within the region
            p_in_region = points_float[i_in_region, :]
            # and get our fit parameters for these peaks
            params_in_region = fit_params[i_in_region, :]

            # find the index of our original peak within the peaks in this sub region
            p_main_ind = np.where(np.all(p_in_region == points_float[i, :], axis=1))[0][0]

            # make sure our main peak is at index 0 (because it's just easier)
            if p_main_ind is not 0:
                p_in_region[[0, p_main_ind]] = p_in_region[[p_main_ind, 0]]
                params_in_region[[0, p_main_ind]] = params_in_region[[p_main_ind, 0]]

            # correct our peak positions to use the region coordinates
            p_in_region -= (p_int - fit_r)

            # now we need to subtract the peaks we aren't going to refine

            # now remove all the extra peaks we have
            for p, param in zip(p_in_region[1:], params_in_region[1:]):
                refine_region -= refine_func(region_coords, *p, *param).reshape(refine_region.shape)

            # now we 'should' only have our peak left that we want to fit
            # so lets do that

            ############################################################################################################
            # Fit bounds
            ############################################################################################################

            bounds_lower, bounds_upper = get_refine_bounds(params_in_region[0], frac_change, peak_type)

            bounds_upper[:2] = points_original[i] - (p_int - fit_r) + move_limit
            bounds_lower[:2] = points_original[i] - (p_int - fit_r) - move_limit

            ############################################################################################################
            # Fitting
            ############################################################################################################

            fit_converged = False

            use_ftol = ftol
            use_gtol = gtol
            use_xtol = xtol

            while not fit_converged:
                try:
                    params_opt, params_cov = curve_fit(refine_func, region_coords, np.ravel(refine_region),
                                                       p0=(*p_in_region[0], *params_in_region[0]),
                                                       bounds=(bounds_lower, bounds_upper), method=fit_method,
                                                       ftol=use_ftol, gtol=use_gtol, xtol=use_xtol)
                    fit_converged = True

                    # get our output coordinates back in the image coords
                    points_float[i] = params_opt[:2] + (p_int - fit_r)

                    # update the parameters for this peak
                    fit_params[i] = params_opt[2:]
                except RuntimeError as e:
                    print("Could not converge fit, reducing fit requirements")
                    use_ftol *= 10
                    use_gtol *= 10
                    use_xtol *= 10
                except ValueError as e:
                    raise e
                except RuntimeWarning as e:
                    raise e

            # so we have fitted one peak!!!
        # so now we have fitted all the peaks (once!)

        # now we could test if we have met some conditions


        # # Option 1:
        # # subtract all the gaussians from the image and sum pixels
        # # can't do this on the entire image quickly, need to only calculate gaussians in local area
        # # could probably do this as we loop through the peaks
        #
        # image_measured = np.zeros_like(data)
        #
        # for i in range(num_points):
        #     p_int = np.round(points_float[i]).astype(np.int)
        #
        #     if (im_dim[1] - r) <= p_int[1] or p_int[1] < r or (im_dim[0] - r) <= p_int[0] or p_int[0] < r:
        #         continue
        #
        #     p = points_float[i] - (p_int - r)
        #
        #     peak_image = refine_func(region_coords, *p, *fit_params[i]).reshape((region_sz, region_sz))
        #
        #     s_y = p_int[0] - r
        #     s_x = p_int[1] - r
        #
        #     f_y = s_y + region_sz
        #     f_x = s_x + region_sz
        #
        #     try:
        #         image_measured[s_y:f_y, s_x:f_x] += peak_image
        #     except e:
        #         raise e

        # Option 2:
        # keep a record of the fitting covariances, and do some sort of sum with then to determine
        # the 'goodness' of the fit

        # total_fit_error = np.mean(np.square(fit_errors)
        # print("Total fit error is: " + str(total_fit_error))

    return points_float


def get_refine_bounds(fit_params, change_frac, peak_type):
    # get total parameters (+ 2 is for y, x)
    total_params = fit_params.size + 2

    # order is y, x, amplitude, sigma, sigma, theta, offset
    bounds_upper = np.full((total_params,), np.inf)
    bounds_lower = np.full((total_params,), -np.inf)

    # first two are the y, x positions. These get set in the main function

    # start by giving some limit on how much anything can change
    bounds_upper[2:] = fit_params * (1 + change_frac)
    bounds_lower[2:] = fit_params * (1 - change_frac)

    if peak_type == PeakType.Gaussian or peak_type == PeakType.Lorentzian:
        theta_ind = 5
    elif peak_type == PeakType.PearsonVII:
        theta_ind = 6

        bounds_upper[3] = np.inf
        bounds_lower[3] = 1.0
    elif peak_type == PeakType.PseudoVoigt:
        theta_ind = 8

        bounds_upper[3] = 1.0
        bounds_lower[3] = 0.0
    else:
        raise Exception("Unknown peak type")

    # set the angle limits (assume default is zero, so make limits symmetric
    # 180 degree range due top symmetry
    bounds_upper[theta_ind] = np.pi / 2
    bounds_lower[theta_ind] = -np.pi / 2

    fit_params[fit_params <= bounds_lower[2:]] += 0.0000001
    fit_params[fit_params >= bounds_upper[2:]] -= 0.0000001

    # bounds_upper[bounds_upper == bounds_lower] += 0.0000001

    return bounds_lower, bounds_upper


def estimate_peak_parameters(data, points_float, r, peak_type):
    # parameters for the twoD_Gaussian fucntion are:
    # xy, xo, yo, amplitude, sigma_x, sigma_y, theta, offset
    # so we need to determine:
    # amplitude, sigma_x, sigma_y, theta, offset

    # get the dimensions of the input image
    im_dim = data.shape

    num_points = points_float.shape[0]

    if peak_type == PeakType.Gaussian or peak_type == PeakType.Lorentzian:
        out_params = np.zeros((num_points, 4))
    elif peak_type == PeakType.PearsonVII:
        out_params = np.zeros((num_points, 5))
    elif peak_type == PeakType.PseudoVoigt:
        out_params = np.zeros((num_points, 7))
    else:
        raise Exception("Unknown peak type")

    bad_points = np.zeros((num_points, 1), dtype='bool')

    for i in range(num_points):
        p_int = np.round(points_float[i, :]).astype(np.int)

        if (im_dim[1] - r) > p_int[1] >= r and (im_dim[0] - r) > p_int[0] >= r:

            # get the region defined by 'r' from the integer peak position
            refine_region = data[(p_int[0] - r):(p_int[0] + r + 1), (p_int[1] - r):(p_int[1] + r + 1)]

            theta = 0
            offset = np.min(refine_region)
            amplitude = refine_region[r, r]

            # now copy to the peak width
            refine_region = normalise_copy(refine_region)

            # sigma is the hard part
            # try to find a HWHM by finding closest pixel that is below half maximum

            # calculate the distance of all pixels from our current point
            region_sz = (2 * r + 1)
            region_coords = np.mgrid[0:region_sz, 0:region_sz]
            distance = np.ravel(np.sqrt(np.square(region_coords[0] - r) + np.square(region_coords[1] - r)))
            # sort by distance
            inds = distance.argsort()
            reg_sort = np.ravel(refine_region)[inds]
            # get lowest value with intensity lower than half max
            half_max = (amplitude - offset) / 2 + offset
            hwhm_ind = np.argmax(reg_sort < half_max)
            # get distance and convert to a standard deviation
            hwhm = distance[inds][hwhm_ind] * 2 / 2.35482

            if hwhm == 0:
                hwhm = 1

            if peak_type == PeakType.Gaussian:
                sigma = hwhm * 2 / 2.35482
                out_params[i, :] = [amplitude, sigma, sigma, theta]
            elif peak_type == PeakType.Lorentzian:
                out_params[i, :] = [amplitude, hwhm, hwhm, theta]
            elif peak_type == PeakType.PearsonVII:
                out_params[i, :] = [amplitude, 5, hwhm, hwhm, theta]
            elif peak_type == PeakType.PseudoVoigt:
                sigma = hwhm * 2 / 2.35482
                out_params[i, :] = [amplitude, 0.5, sigma, sigma, hwhm, hwhm, theta]
        else:
            bad_points[i] = True

    out_points = points_float[np.where(np.logical_not(bad_points))[0], :]
    out_params = out_params[np.where(np.logical_not(bad_points))[0], :]

    return out_points, out_params


def do_fitting_gauss(data, points, fit_r=10, contribute_r=20,
                     iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
    image = normalise_copy(data)

    peak_type = PeakType.Gaussian

    culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)

    func = gaussian_2d
    return refine_fitting(image, culled_peaks, params, func,
                          fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)


def do_fitting_lorentz(data, points, fit_r=10, contribute_r=20,
                       iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
    image = normalise_copy(data)

    peak_type = PeakType.Lorentzian

    culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)

    func = lorentz_2d
    return refine_fitting(image, culled_peaks, params, func,
                          fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)


def do_fitting_pearson_vii(data, points, fit_r=10, contribute_r=20,
                           iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
    image = normalise_copy(data)

    peak_type = PeakType.PearsonVII

    culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)

    func = pearson_vii_2d
    return refine_fitting(image, culled_peaks, params, func,
                          fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)


def do_fitting_voigt(data, points, fit_r=10, contribute_r=20,
                     iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
    image = normalise_copy(data)

    peak_type = PeakType.PseudoVoigt

    culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)

    func = pseudo_voigt_2d
    return refine_fitting(image, culled_peaks, params, func,
                          fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)
