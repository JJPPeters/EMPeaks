import numpy as np
from scipy.optimize import curve_fit
from scipy import ndimage
from enum import Enum

from Processing.Utilities import gaussian_2d, lorentz_2d, pearson_vii_2d, pseudo_voigt_2d
from Processing.Utilities import gaussian_2d_fitting
from Processing.Utilities import normalise_copy

from lmfit import Model, Parameter




#
#
#
# def do_fitting_gauss_2(data, points, fit_r=10, contribute_r=20,
#                       iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
#     image = normalise_copy(data)
#
#     peak_type = PeakType.Gaussian
#     # peak_type = PeakType.Lorentzian
#     # peak_type = PeakType.PearsonVII
#     # peak_type = PeakType.PseudoVoigt
#
#     # culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)
#     initial_params = estimate_gauss_parameters(image, points, fit_r, lim)
#
#     func = gaussian_2d_fitting
#     # func = lorentz_2d
#     # func = pearson_vii_2d
#     # func = pseudo_voigt_2d
#     test = refine_fitting_2(image, points, initial_params, func, fit_r, lim, peak_type, fit_method)
#     return test





# def get_refine_bounds(fit_params, change_frac, peak_type):
#     # get total parameters (+ 2 is for y, x)
#     total_params = fit_params.size + 2
#
#     # order is y, x, amplitude, sigma, sigma, theta, offset
#     bounds_upper = np.full((total_params,), np.inf)
#     bounds_lower = np.full((total_params,), -np.inf)
#
#     # first two are the y, x positions. These get set in the main function
#
#     # start by giving some limit on how much anything can change
#     if change_frac == np.inf:
#         bounds_upper[2:] = np.inf
#         bounds_lower[2:] = -np.inf
#     else:
#         bounds_upper[2:] = fit_params + np.abs(fit_params) * change_frac
#         bounds_lower[2:] = fit_params - np.abs(fit_params) * change_frac
#
#     if peak_type == PeakType.Gaussian or peak_type == PeakType.Lorentzian:
#         theta_ind = 5
#
#         # amplitude
#         bounds_lower[2] = np.max([0.0, bounds_lower[2]])
#
#         # sigma or gamma
#         bounds_lower[3] = np.max([0.0000001, bounds_lower[4]])
#         bounds_lower[4] = np.max([0.0000001, bounds_lower[5]])
#
#     elif peak_type == PeakType.PearsonVII:
#         theta_ind = 6
#
#         bounds_upper[3] = np.inf
#         bounds_lower[3] = 1.0
#     elif peak_type == PeakType.PseudoVoigt:
#         theta_ind = 8
#
#         # gaussian sigma
#         bounds_lower[4] = np.max([0.0000001, bounds_lower[4]])
#         bounds_lower[5] = np.max([0.0000001, bounds_lower[5]])
#
#         # lorentz
#         bounds_lower[6] = np.max([0.0000001, bounds_lower[6]])
#         bounds_lower[7] = np.max([0.0000001, bounds_lower[7]])
#
#         # amplitude
#         bounds_lower[2] = np.max([0.0, bounds_lower[2]])
#
#         # this is the fraction of guass/lorentz
#         bounds_upper[3] = 1.0
#         bounds_lower[3] = 0.0
#     else:
#         raise Exception("Unknown peak type")
#
#     # set the angle limits (assume default is zero, so make limits symmetric
#     # 180 degree range due top symmetry
#     bounds_upper[theta_ind] = np.pi / 2
#     bounds_lower[theta_ind] = -np.pi / 2
#
#     fit_params[fit_params <= bounds_lower[2:]] += 0.0000001
#     fit_params[fit_params >= bounds_upper[2:]] -= 0.0000001
#
#     # bounds_upper[bounds_upper == bounds_lower] += 0.0000001
#
#     return bounds_lower, bounds_upper



























# def do_fitting_gauss(data, points, fit_r=10, contribute_r=20,
#                      iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
#     image = normalise_copy(data)
#
#     peak_type = PeakType.Gaussian
#
#     culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)
#
#     func = gaussian_2d
#     return refine_fitting(image, culled_peaks, params, func,
#                           fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)
#
#
# def do_fitting_lorentz(data, points, fit_r=10, contribute_r=20,
#                        iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
#     image = normalise_copy(data)
#
#     peak_type = PeakType.Lorentzian
#
#     culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)
#
#     func = lorentz_2d
#     return refine_fitting(image, culled_peaks, params, func,
#                           fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)
#
#
# def do_fitting_pearson_vii(data, points, fit_r=10, contribute_r=20,
#                            iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
#     image = normalise_copy(data)
#
#     peak_type = PeakType.PearsonVII
#
#     culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)
#
#     func = pearson_vii_2d
#     return refine_fitting(image, culled_peaks, params, func,
#                           fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)
#
#
# def do_fitting_voigt(data, points, fit_r=10, contribute_r=20,
#                      iterations=2, lim=1, frac_change=0.3, fit_method='trf'):
#     image = normalise_copy(data)
#
#     peak_type = PeakType.PseudoVoigt
#
#     culled_peaks, params = estimate_peak_parameters(image, points, fit_r, peak_type)
#
#     func = pseudo_voigt_2d
#     return refine_fitting(image, culled_peaks, params, func,
#                           fit_r, contribute_r, iterations, lim, frac_change, fit_method, peak_type)
