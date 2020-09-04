import numpy as np


def estimate_peak_parameters(refine_region, r):
    # we need to determine (for our fitting)
    # amplitude, sigma, offset

    # get a very simple estimate of the bacground
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