import numpy as np
from collections import OrderedDict
from itertools import islice
import math


class IndexedDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(IndexedDict, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        if isinstance(key, int):
            return next(islice(self.values(), key, None))

        return super(IndexedDict, self).__getitem__(key)


def normalise_in_place(data):
    data -= np.amin(data)
    data /= np.amax(data)


# TODO: could add some test that our rnages are sensible? (could also type hint)
def normalise_copy(data, in_range=None, out_range=None, clip=True):
    new = data.astype(np.float64)
    if in_range is not None:
        new -= in_range[0]
    else:
        new -= np.amin(new)

    if np.amax(new) == 0:  # have an array of zeros
        return data
    if in_range is not None:
        new /= in_range[1]
    else:
        v = np.amax(new)
        new = np.divide(new, v, out=np.zeros_like(new), where=v != 0)

    if in_range is not None and clip:
        new = np.clip(new, in_range[0], in_range[1])

    if out_range is not None:
        new *= out_range[1]
        new += out_range[0]

    return new


def remove_duplicates(data):
    return np.unique(data, axis=0)


def get_perentage_sample(data, percent):
    # percent as fraction
    percent *= 100
    tp = percent
    fp = 100 - percent
    temp = [True]*tp + [False]*fp
    sample = np.random.choice(temp, data.shape)
    return data[sample]


def get_grid_sample_divisions(data, grid_samples):
    spacing = np.ceil(np.array(data.shape) / grid_samples).astype(np.uint32)
    return data[0::spacing[0], 0::spacing[1]]


def get_grid_sample_spacing(data, grid_spacing):
    return data[0::grid_spacing, 0::grid_spacing]


def slow_sum_nth_elements(a, n: int, axis: int = 0):
    def axis_func(a, n):
        sz = a.size

        # // is a floor divide
        bin = (np.arange(a.size) // n).astype(np.int)

        return np.bincount(bin, a)

    fnc = lambda ar: axis_func(ar, n)

    test = np.apply_along_axis(fnc, axis, a)

    return test


def average_nth_elements(a, n: int, axis: int = 0, sum: bool = False):
    ndim = a.ndim

    # account for when the axis isn't an integer number of n long
    if a.shape[axis] % n != 0:
        pd = [[0, 0] for x in range(ndim)]
        pd[axis][1] = n - a.shape[axis] % n

        # first pad array to be a multiple of n
        a = np.pad(a.astype(np.float32), pd, mode='constant', constant_values=np.NaN)

    # for the sum to work properly, have to move our axis of interest to last
    a = np.swapaxes(a, axis, -1)

    # get the new shape
    new_shp = list(a.shape)
    new_shp[-1] = int(new_shp[-1] / n)
    new_shp.append(n)

    # do the average
    if sum:
        new_a = np.nansum(a.reshape(new_shp), axis=ndim)
    else:
        new_a = np.nanmean(a.reshape(new_shp), axis=ndim)

    # move our axis back and return
    return np.swapaxes(new_a, axis, -1)


def pad_to_multiple_of_2(a, axes=None):
    n = 2
    pd = [[0, 0] for x in range(a.ndim)]

    for ax in axes:
        sz = a.shape[ax]
        if sz % n != 0:
            pd[ax][1] = n - a.shape[ax] % n

    if np.all(pd == 0):
        return a
    else:
        return np.pad(a, pd, mode='edge')


def pad_to_power_of_2(a, axes=None):

    pd = [[0, 0] for x in range(a.ndim)]

    for ax in axes:
        sz = a.shape[ax]
        n = 2**math.ceil(math.log(sz, 2))
        if sz % n != 0:
            pd[ax][1] = n - a.shape[ax] % n

    if np.all(pd == 0):
        return a
    else:
        return np.pad(a, pd, mode='constant', constant_values=0)
