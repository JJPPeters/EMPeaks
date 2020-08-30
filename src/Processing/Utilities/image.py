import numpy as np
from scipy.special import comb
from .peak_functions import gaussian_2d


# this is sort of supposed to be used like the gaussian option of fspecial in matlab
def gaussian_2d_simple(size, sigma, norm=True):
    r = np.floor(size / 2).astype(np.int32)
    yx = np.mgrid[0:size, 0:size] - r

    out = gaussian_2d(yx, 0, 0, 1, sigma, sigma, do_ravel=False)
    if norm:
        out /= np.sum(out)

    return out


def disc_2d(size):
    r = np.floor(size / 2).astype(np.int32)
    yx = np.mgrid[0:size, 0:size] - r

    out = (yx[0]**2 + yx[1]**2) < 1

    return out.astype(np.float64)


def hann_window(image):
    w1 = np.hanning(image.shape[0])
    w2 = np.hanning(image.shape[1])

    window = np.einsum('i,j->ij', w1, w2)

    return np.multiply(image, window)


# https://stackoverflow.com/a/45166120
def smooth_step(x, x_min=0, x_max=1, smooth=1):
    x = np.clip((x - x_min) / (x_max - x_min), 0, 1)

    result = 0
    for n in range(0, smooth + 1):
        result += comb(smooth + n, n) * comb(2 * smooth + 1, smooth - n) * (-x) ** n

    result *= x ** (smooth + 1)

    return result


def smooth_circle_like(in_image, centre_x, centre_y, radius_in, radius_out):
    start_x = -centre_x
    end_x = in_image.shape[1] - centre_x
    start_y = -centre_y
    end_y = in_image.shape[0] - centre_y

    x = np.linspace(start_x, end_x, in_image.shape[1])
    y = np.linspace(start_y, end_y, in_image.shape[0])
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx**2 + yy**2)
    return (-1 * smooth_step(r, radius_in, radius_out)) + 1