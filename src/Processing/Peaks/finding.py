import numpy as np
import itertools
from Processing.Utilities import remove_duplicates, hann_window, normalise_copy

from scipy.spatial.distance import cdist

from skimage.feature import peak_local_max


def detect_local_maxima(img, min_dist=0, thresh=0.0):
    image = img.copy()

    image_min = np.min(image)
    image_range = np.max(image) - image_min
    min_intens = thresh * image_range + image_min

    p = peak_local_max(image, min_distance=min_dist, threshold_abs=min_intens, exclude_border=True)

    c1 = image[p[:, 0], p[:, 1]] > image[p[:, 0] + 1, p[:, 1]]
    c2 = image[p[:, 0], p[:, 1]] > image[p[:, 0] - 1, p[:, 1]]
    c3 = image[p[:, 0], p[:, 1]] > image[p[:, 0], p[:, 1] + 1]
    c4 = image[p[:, 0], p[:, 1]] > image[p[:, 0], p[:, 1] - 1]

    peaks = p[np.where(np.logical_and.reduce((c1, c2, c3, c4)))[0]]

    return peaks



# def detect_local_maxima(arr):
#     neighborhood = ndimage.generate_binary_structure(len(arr.shape), 2)
#     local_max = (ndimage.maximum_filter(arr, footprint=neighborhood) == arr)
#     background = (arr == 0)
#     eroded_background = ndimage.morphology.binary_erosion(
#         background, structure=neighborhood, border_value=1)
#     detected_maxima = local_max - eroded_background
#     tup = np.where(detected_maxima)
#     tup[0].shape = (tup[0].size, 1)
#     tup[1].shape = (tup[1].size, 1)
#     return np.column_stack(tup)

def average_nearby_peaks(data, ps, r=5):
    # make these now, they won't be all used, but they will be bigger than the output so can just crop
    points = ps.astype('float64')
    new_points = np.empty_like(points, dtype='float64')

    dists = cdist(points, points, 'Euclidean')

    new_cnt = 0
    for i, ds in enumerate(dists):
        close_inds = np.where(ds < r)[0]
        close_points = points[close_inds, :]

        if close_points.shape[0] > 1:

            mass = data[close_points[:, 0].astype(np.int32), close_points[:, 1].astype(np.int32)]

            cent = np.mean(close_points * mass, axis=0) / np.sum(mass)

            new_points[new_cnt, :] = cent[:]
        else:
            new_points[new_cnt] = points[i, :]
        new_cnt += 1

    return remove_duplicates(new_points[:new_cnt])

def estimate_lattice_vectors(image):
    # 1. FFT (power spectrum) with hann window
    pow_spec = np.log(np.abs(np.fft.fftshift(np.fft.fft2(hann_window(image)))) + 1)

    # 2. Get mexima - restrict radius AND restrict intensity
    peaks = detect_local_maxima(pow_spec, 5, 0.5)

    mid = np.array(image.shape) / 2

    rad = np.sqrt(np.sum(np.square(peaks - np.floor(mid)), axis=1))
    lim = np.min(mid)
    cropped_inds = np.where(np.logical_and(rad < lim, rad > 5))

    cropped_peaks = peaks[cropped_inds]

    # TODO: It's an FFT, so we can remove half the image anyway

    # 3. take top 20 ? peaks by intensity
    top_n = 20
    intens = pow_spec[cropped_peaks[:, 0], cropped_peaks[:, 1]]
    top_inds = np.argpartition(intens, intens.size-top_n)[-top_n:]

    cropped_peaks = cropped_peaks[top_inds, :]

    best_score = -1

    # 4. loop through all our combinations
    for combination in itertools.combinations(cropped_peaks, 2):
        if np.all(combination[0] == combination[1]):
            continue

        v1 = combination[0] - mid.astype(np.int)
        v2 = combination[1] - mid.astype(np.int)

        area = np.abs(np.linalg.det([v1, v2]))

        # TODO: these tests need to be more though out (I use guesses for 'sensible' values)
        # idea is to remove peaks that are collinear
        if np.sum(v1 + v2) < 10 or area < image.shape[0] * image.shape[1] * 0.001:
            continue

        # generate lattice filling the image
        # do naively, i.e. we won't always fill the image guaranteed

        rnge = 5
        v_intens = []
        for lattice in itertools.combinations(np.arange(-rnge, rnge+1), 2):
            v = mid.astype(np.int) + v1*lattice[0] + v2*lattice[1]

            if np.sqrt(np.sum(np.square(v))) > lim:
                continue

            if np.all([v >= np.array([0, 0]), v < np.array(pow_spec.shape)]):
                v_intens.append(np.sum(pow_spec[v[0]-2:v[0]+3, v[1]-2:v[1]+3]))

        if len(v_intens) == 0:
            continue

        mag_1 = np.sum(np.square(v1))
        mag_2 = np.sum(np.square(v2))

        # variables to play with, area, vector magnitude, intensity of lattice, number of points in range
        score = np.median(v_intens) / (mag_1 * mag_2)

        if score > best_score:
            best_score = score
            best_combination = combination

    lattice_peaks = np.zeros((3, 2))

    lattice_peaks[0, :] = mid.astype(np.int)
    lattice_peaks[1, :] = best_combination[0]
    lattice_peaks[2, :] = best_combination[1]

    return pow_spec, lattice_peaks