import numpy as np


########################################################################################################################
# gaussian_2d
########################################################################################################################
# Inputs
#
# yx - list-like of (y, x) coordinates
# y0 - peak y position
# x0 - peak x position
# amplitude - height of the peak
# sigma_x - standard deviation in x direction
# sigma_y - standard deviation in y direction
# theta - rotation of the peak
# offset - baseline of peak
# do_ravel - return output as list like (for curve_fit)
########################################################################################################################
# https://stackoverflow.com/questions/21566379/fitting-a-2d-gaussian-function-using-scipy-optimize-curve-fit-valueerror-and-m
########################################################################################################################
def gaussian_2d(yx, yo, xo, amplitude, sigma_x, sigma_y, theta=0.0, offset=0.0, do_ravel=True):
    x = yx[1]
    y = yx[0]

    cs = np.cos(theta)
    sn = np.sin(theta)
    sn2 = np.sin(2*theta)

    a = cs**2 / (2 * sigma_x**2) + sn**2 / (2 * sigma_y**2)
    b = -sn2 / (4 * sigma_x**2) + sn2 / (4 * sigma_y**2)
    c = sn**2 / (2 * sigma_x**2) + cs**2 / (2 * sigma_y**2)

    gauss = offset + amplitude * np.exp(-(a * ((x - xo)**2) + 2 * b * (x - xo) * (y - yo) + c * ((y - yo)**2)))

    # x = cs * (yx[1] - xo) - sn * (yx[0] - yo)
    # y = sn * (yx[1] - xo) + cs * (yx[0] - yo)
    #
    # gauss = offset + amplitude * np.exp(-0.5 * ((x * x) / (2 * sigma_x * sigma_x) + (y * y) / (2 * sigma_y * sigma_y)))
    if do_ravel:
        return gauss.ravel()
    else:
        return gauss


########################################################################################################################
# lorentz_2d
########################################################################################################################
# Inputs
#
# yx - list-like of (y, x) coordinates
# y0 - peak y position
# x0 - peak x position
# amplitude - height of the peak
# gamma_x - HWHM in x direction
# gamma_y - HWHM in y direction
# theta - rotation of the peak
# offset - baseline of peak
# do_ravel - return output as list like (for curve_fit)
########################################################################################################################
# https://stackoverflow.com/questions/21566379/fitting-a-2d-gaussian-function-using-scipy-optimize-curve-fit-valueerror-and-m
########################################################################################################################
def lorentz_2d(yx, yo, xo, amplitude, gamma_x, gamma_y, theta=0.0, offset=0.0, do_ravel=True):
    cs = np.cos(theta)
    sn = np.sin(theta)

    x = cs * (yx[1] - xo) - sn * (yx[0] - yo)
    y = sn * (yx[1] - xo) + cs * (yx[0] - yo)

    ratio = gamma_x / gamma_y
    y = y * ratio

    lorentz = offset + amplitude * (gamma_x * gamma_x / (x ** 2 + y ** 2 + gamma_x * gamma_x))

    if do_ravel:
        return lorentz.ravel()
    else:
        return lorentz


########################################################################################################################
# pearson_vii_2d
########################################################################################################################
# Inputs
#
# yx - list-like of (y, x) coordinates
# y0 - peak y position
# x0 - peak x position
# amplitude - height of the peak
# w_x - width in x direction
# w_y - width in y direction
# m - how lorentz like (m=1) or gaussian line (m=inf)
# theta - rotation of the peak
# offset - baseline of peak
# do_ravel - return output as list like (for curve_fit)
########################################################################################################################
# http://pd.chem.ucl.ac.uk/pdnn/peaks/pvii.htm
########################################################################################################################
def pearson_vii_2d(yx, yo, xo, amplitude, m, w_x, w_y, theta=0.0, offset=0.0, do_ravel=True):
    cs = np.cos(theta)
    sn = np.sin(theta)

    x = cs * (yx[1] - xo) - sn * (yx[0] - yo)
    y = sn * (yx[1] - xo) + cs * (yx[0] - yo)

    ratio = w_x / w_y
    y = y * ratio

    pearsons = offset + amplitude * (w_x ** (2 * m)) / (w_x ** 2 + (2 ** (1 / m) - 1) * (x ** 2 + y ** 2)) ** m
    if do_ravel:
        return pearsons.ravel()
    else:
        return pearsons


########################################################################################################################
# pseudo_voigt_2d
########################################################################################################################
# Inputs
#
# yx - list-like of (y, x) coordinates
# y0 - peak y position
# x0 - peak x position
# amplitude - height of the peak
# frac - fraction of lorentz (frac=1) to gauss (frac=0)
# sigma_x - standard deviation in x direction
# sigma_y - standard deviation in y direction
# gamma_x - HWHM in x direction
# gamma_y - HWHM in y direction
# theta - rotation of the peak
# offset - baseline of peak
# do_ravel - return output as list like (for curve_fit)
########################################################################################################################
# http://pd.chem.ucl.ac.uk/pdnn/peaks/others.htm
########################################################################################################################
def pseudo_voigt_2d(yx, yo, xo, amplitude, frac, sigma_x, sigma_y, gamma_x, gamma_y,
                    theta=0.0, offset=0.0, do_ravel=True):
    cs = np.cos(theta)
    sn = np.sin(theta)

    x = cs * (yx[1] - xo) - sn * (yx[0] - yo)
    y = sn * (yx[1] - xo) + cs * (yx[0] - yo)

    gauss = offset + amplitude * np.exp(-((x * x) / (2 * sigma_x * sigma_x) + (y * y) / (2 * sigma_y * sigma_y)))

    ratio = gamma_x / gamma_y
    y = y * ratio

    lorentz = (gamma_x * gamma_x / (x ** 2 + y ** 2 + gamma_x * gamma_x))

    voigt = offset + amplitude * (frac * lorentz + (1-frac) * gauss)
    if do_ravel:
        return voigt.ravel()
    else:
        return voigt
