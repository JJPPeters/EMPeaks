import numpy as np
from scipy import ndimage
from Processing.Utilities import normalise_copy


########################################################################################################################
# refine_generic
########################################################################################################################
# Inputs
#
# data - the image the points are to be refined using
# float_points - list of positions as floats, each row being [y, s]
# refine_func - function that takes an image and the refine_args/kwargs and returns a refined coord within that image
# r - 'radius' to using from peak for refining (uses square, not circle)
# lim - limit of movement after refinement
# refine_args/kwargs - arguments used for fitting
########################################################################################################################
def refine_generic(data, float_points, refine_func, r=1, lim=1, *refine_args, **refine_kwargs):
    points = np.round(float_points).astype(int)
    # convenience
    sz = points.shape[0]
    # create arrays for output, 'bad' points will be removed later
    out_xy = np.zeros(shape=(sz, 2), dtype='Float64')  # xy
    # to use for determining edges
    dim = data.shape
    # to be filled with index of points to remove (i.e. close to edge)
    bad_points = []
    # just for counting unrefined positions
    n_outside_lims = 0
    n_unrefined = 0

    for i in range(sz):
        # for convenience
        a = int(points[i, 1])  # x
        b = int(points[i, 0])  # y

        if (dim[1] - r) > a >= r and (dim[0] - r) > b >= r:  # if points are not in the edge
            # shift calculated from provided function
            # note that the mid point/radius must be subtracted
            shift, valid = refine_func(data[(b - r):(b + r + 1), (a - r):(a + r + 1)], *refine_args, **refine_kwargs)
            shift -= r

            if valid and (lim == 0 or (abs(shift[0]) < lim and abs(shift[1]) < lim)):
                out_xy[i, :] = points[i, :] + shift  # xy
            elif valid:
                out_xy[i, :] = points[i, :]
                n_outside_lims += 1
            else:
                out_xy[i, :] = points[i, :]
                n_unrefined += 1
        else:
            # build list of points at edge here.
            bad_points.append(i)

        # remove our bad points and get new size
    out_xy = np.delete(out_xy, bad_points, 0)

    return out_xy, (n_outside_lims, n_unrefined, len(bad_points))


########################################################################################################################
# maximum
########################################################################################################################
# moves peak to maximum pixel in local area
########################################################################################################################
def maximum_func(region, *args, **kwargs):
    return np.array(np.unravel_index(np.argmax(region), region.shape)), True


def do_maximum(data, points, r=1, lim=1):
    func = maximum_func
    return refine_generic(data, points, func, r=r, lim=lim)


########################################################################################################################
# centroid
########################################################################################################################
# moves peak to centroid of local area
########################################################################################################################
def centroid_func(region, *args, **kwargs):
    normalise = kwargs.get('normalise')
    if normalise:
        region = normalise_copy(region)

    return np.array(ndimage.center_of_mass(region)), True


def do_centroid(data, points, r=1, lim=1, normalise=True):
    func = centroid_func
    return refine_generic(data, points, func, r=r, lim=lim, normalise=normalise)


########################################################################################################################
# interpolation
########################################################################################################################
# interpolates local area and moves peak to the new maximum
########################################################################################################################
def interp_func(region, *args, **kwargs):
    zoom = kwargs.get('zoom')
    order = kwargs.get('order')

    zoomed = ndimage.zoom(region, zoom, output=np.float64, order=order)
    ii, ij = np.unravel_index(zoomed.argmax(), zoomed.shape)

    # assumes region is SQUARE
    scale = (region.shape[0] * zoom - 1) / (region.shape[0] - 1)
    return np.array([ii, ij]) / scale, True


def do_interp(data, points, r=1, lim=1, zoom=20, order=3):
    func = interp_func
    return refine_generic(data, points, func, r=r, lim=lim, zoom=zoom, order=order)


########################################################################################################################
# parabola
########################################################################################################################
# fits parabola in x and y to find maximum
########################################################################################################################
def parabola_func(region, *args, **kwargs):
    order = kwargs.get('order')

    mid = int((region.shape[0] - 1) / 2)
    x_strip = region[mid, :]
    y_strip = region[:, mid]

    # before, use this function (might still be faster, but more limited)
    # fit_3_point_parabola(x_strip)

    index = np.arange(region.shape[0])

    try:
        x_fit = np.polyfit(index, x_strip, deg=order)
        x_mid = - x_fit[1] / (2 * x_fit[0])
    except np.RankWarning:
        return np.array([mid, mid]), False

    try:
        y_fit = np.polyfit(index, y_strip, deg=order)
        y_mid = - y_fit[1] / (2 * y_fit[0])
    except np.RankWarning:
        return np.array([mid, mid]), False

    return np.array([x_mid, y_mid]), True


def do_parabola(data, points, r=1, lim=1, order=2):
    func = parabola_func
    return refine_generic(data, points, func, r=r, lim=lim, order=order)