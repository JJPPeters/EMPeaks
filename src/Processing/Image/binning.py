import numpy as np

from Processing.Utilities.arrays import average_nth_elements


def bin_image(image, binnings):

    n_ax = len(binnings)

    binned_image = np.copy(image)

    for i in range(n_ax):
        n = binnings[i]
        if n != 1:
            binned_image = average_nth_elements(binned_image, n, i)

    # sx = image.shape[0]
    # sy = image.shape[1]
    #
    # nx = int(sx / x_bin)
    # ny = int(sy / y_bin)
    #
    # if image.ndim > 2:
    #     sz = image.shape[2]
    #     binned_image = np.zeros((nx, ny, sz))
    #     for i in range(sz):
    #         binned_image[:, :, i] = do_binning_slice(image[:, :, i], x_bin, y_bin, nx, ny)
    # else:
    #     binned_image = do_binning_slice(image, x_bin, y_bin, nx, ny)

    return binned_image


def do_binning_slice(image, x_bin, y_bin, nx, ny):
    if x_bin > 1:
        x_bin_image = np.zeros((nx, image.shape[1]))
        for i in range(0, nx):
            x_bin_image[i, :] = np.sum(image[i * x_bin:(i + 1) * x_bin, :], axis=0)
    else:
        x_bin_image = image

    if y_bin > 1:
        y_bin_image = np.zeros((nx, ny))
        for i in range(0, ny):
            y_bin_image[:, i] = np.sum(x_bin_image[:, i * y_bin:(i + 1) * y_bin], axis=1)
    else:
        y_bin_image = x_bin_image

    return y_bin_image


def unbin_image(image, x_bin, y_bin):
    sx = image.shape[0]
    sy = image.shape[1]

    nx = int(sx * x_bin)
    ny = int(sy * y_bin)

    if image.ndim > 2:
        sz = image.shape[2]
        binned_image = np.zeros((nx, ny, sz))
        for i in range(sz):
            binned_image[:, :, i] = do_unbinning_slice(image[:, :, i], x_bin, y_bin)
    else:
        binned_image = do_unbinning_slice(image, x_bin, y_bin)

    return binned_image


def do_unbinning_slice(image, x_bin, y_bin):
    if x_bin > 1:
        x_bin_image = np.repeat(image, x_bin, axis=0)
    else:
        x_bin_image = image

    if y_bin > 1:
        y_bin_image = np.repeat(x_bin_image, y_bin, axis=1)
    else:
        y_bin_image = x_bin_image

    return y_bin_image / (x_bin * y_bin)
