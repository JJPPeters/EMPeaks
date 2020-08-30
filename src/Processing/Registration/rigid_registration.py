import numpy as np
from skimage.registration._phase_cross_correlation import _upsampled_dft
from scipy.ndimage import interpolation
from scipy import signal


# ripped straight from scikit-image
def cross_correlate(src_image, target_image, upsample_factor=100, hann_window=True):
    # shifts are calculated as source to reference

    if hann_window:
        w1 = np.hanning(src_image.shape[0])
        w2 = np.hanning(src_image.shape[1])

        window = np.einsum('i,j->ij',w1,w2)

        src_image = np.multiply(src_image, window)
        target_image = np.multiply(target_image, window)

    # fft our data
    src_freq = np.fft.fftn(src_image)
    target_freq = np.fft.fftn(target_image)

    # do the cross correlation multiplicaion
    shape = src_freq.shape
    image_product = np.multiply(src_freq, target_freq.conj())

    # back to real space
    cross_correlation = np.fft.ifftn(image_product)

    # this doesn't work due to the sub pixel part
    # if shift_limit > 0:
    #     # apply our shift limit here
    #     Y, X = np.ogrid[:shape[0], :shape[1]]
    #     center = np.array(shape) / 2
    #     dist_from_center = np.sqrt((X - center[1]) ** 2 + (Y - center[0]) ** 2)
    #     mask = np.fft.fftshift(dist_from_center <= shift_limit)
    #
    #     cross_correlation = np.multiply(cross_correlation, mask)


    # back to the scikit image bit
    maxima = np.unravel_index(np.argmax(np.abs(cross_correlation)),
                              cross_correlation.shape)
    midpoints = np.array([np.fix(axis_size / 2) for axis_size in shape])

    shifts = np.array(maxima, dtype=np.float64)

    shifts[shifts > midpoints] -= np.array(shape)[shifts > midpoints]

    if upsample_factor > 1:
        # Initial shift estimate in upsampled grid
        shifts = np.round(shifts * upsample_factor) / upsample_factor
        upsampled_region_size = np.ceil(upsample_factor * 1.5)
        # Center of output array at dftshift + 1
        dftshift = np.fix(upsampled_region_size / 2.0)
        upsample_factor = np.array(upsample_factor, dtype=np.float64)
        normalization = (src_freq.size * upsample_factor ** 2)
        # Matrix multiply DFT around the current shift estimate
        sample_region_offset = dftshift - shifts * upsample_factor
        cross_correlation = _upsampled_dft(image_product.conj(),
                                           upsampled_region_size,
                                           upsample_factor,
                                           sample_region_offset).conj()
        cross_correlation /= normalization
        # Locate maximum and map back to original pixel grid
        maxima = np.array(np.unravel_index(
            np.argmax(np.abs(cross_correlation)),
            cross_correlation.shape),
            dtype=np.float64)
        maxima -= dftshift

        shifts = shifts + maxima / upsample_factor

        # If its only one row or column the shift along that dimension has no
        # effect. We set to zero.
    for dim in range(src_freq.ndim):
        if shape[dim] == 1:
            shifts[dim] = 0

    return shifts  # (y, x) shifts


def interpolate_shift(im, shift):
    # cval is the background
    # order is the order of the interpolation
    return interpolation.shift(im, shift, mode='constant', cval=0, order=1)


def rigid_align(image, reference_frame=None, average_reference=True, crop_stack=True, align_stack=True, average_stack=True):

    # measure the shifts
    return_dict = register_rigid_translate(image, reference_frame, average_reference, align_stack or average_stack)

    if crop_stack and (align_stack or average_stack):

        aligned_stack = return_dict['aligned_stack']
        cum_shifts = return_dict['cumulative_shifts']

        # get min and max shifts
        mn = cum_shifts.min(axis=0)
        mx = cum_shifts.max(axis=0)

        # round properly (to largest absolute value)
        mn = np.multiply(np.rint(mn), np.sign(mn)).astype(int)
        mx = np.multiply(np.rint(mx), np.sign(mx)).astype(int)

        sx = aligned_stack.shape[1]
        sy = aligned_stack.shape[0]

        return_dict['aligned_stack'] = aligned_stack[mx[0]:sx-mn[0], mx[1]:sy-mn[1], :]

    if average_stack:
        return_dict['averaged_stack'] = np.mean(return_dict['aligned_stack'], axis=2)

    return return_dict


def register_rigid_translate(image, reference_frame, average_reference=True, align_stack=True):
    sz = image.shape[2]  # quality of life
    cumulative_shifts = np.zeros((sz, 2))  # to store our shifts

    # make our algined stack output if we need it
    if align_stack:
        aligned = np.zeros_like(image)

    # set our reference frame if we want a running average
    if average_reference:
        if reference_frame is None:
            reference_frame = 0  # because with running average, this is the same (and easier to code or just one case)
        align_stack = True  # because we need this to get the running average

    # copy our reference frame
    if reference_frame is not None:
        reference = np.copy(image[:, :, reference_frame])

    i = 0
    while i < sz:
        # for our reference frame, just copy it across and move on (this loop still completes, just increment i)
        if reference_frame == i or (reference_frame is None and i == 0):
            if align_stack:
                aligned[:, :, i] = image[:, :, i]
            i += 1  # just do the next frame already (this one has shift 0)

        # this is so we can calculate an average (not just a sum) as we add to our average
        n = 1
        if average_reference:
            n = i

        # calculate the shifts
        cumulative_shifts[i, :] = -1 * cross_correlate(image[:, :, i], reference / n)

        # update our stack and/or the average image
        if align_stack or average_reference:
            shifted = interpolate_shift(image[:, :, i], cumulative_shifts[i, :])
            if align_stack:
                aligned[:, :, i] = shifted
            if average_reference:
                reference += aligned[:, :, i]  # how do the edge/shifted averaged affect the use of this reference?

        i += 1

    outputs = {'cumulative_shifts': cumulative_shifts}

    if align_stack:
        outputs['aligned_stack'] = aligned

    return outputs


def overdetermined_rigid_align(image, crop_stack=True, align_stack=True, average_stack=True):
    # measure the shifts
    return_dict = register_rigid_translate_overdetermined(image, align_stack or average_stack)

    if crop_stack and (align_stack or average_stack):

        aligned_stack = return_dict['aligned_stack']
        cum_shifts = return_dict['cumulative_shifts']

        # get min and max shifts
        mn = cum_shifts.min(axis=0)
        mx = cum_shifts.max(axis=0)

        # round properly (to largest absolute value)
        mn = np.multiply(np.rint(mn), np.sign(mn)).astype(int)
        mx = np.multiply(np.rint(mx), np.sign(mx)).astype(int)

        sx = aligned_stack.shape[1]
        sy = aligned_stack.shape[0]

        return_dict['aligned_stack'] = aligned_stack[mx[0]:sx-mn[0], mx[1]:sy-mn[1], :]

    if average_stack:
        return_dict['averaged_stack'] = np.mean(return_dict['aligned_stack'], axis=2)

    return return_dict


def register_rigid_translate_overdetermined(stack, align_stack=True):
    # number of frames
    n = stack.shape[2]

    # number of equations
    m = int((n-1)*n/2)

    r = np.zeros((n-1, 2))
    b = np.zeros((m, 2))
    A = np.zeros((m, n-1))

    count = 0  # for easier indexing
    for i in range(n):
        for j in range(i+1, n):
            if j == i:
                pass

            b[count] = cross_correlate(stack[:, :, i], stack[:, :, j])

            if j == i+1:
                r[i] = b[count]

            for k in range(i, j):
                A[count, k] = 1.0

            count += 1

    r_s = np.dot(np.dot(np.linalg.inv(np.dot(A.T, A)), A.T), b)

    aligned = np.zeros_like(stack)
    aligned[:, :, 0] = stack[:, :, 0]

    for i in range(1, n):
        aligned[:, :, i] = interpolate_shift(stack[:, :, i], r_s[i-1])

    outputs = {'cumulative_shifts': r_s}

    if align_stack:
        outputs['aligned_stack'] = aligned

    return outputs

def pyramid_rigid_align(image, pyramid_size=3, crop_stack=True, align_stack=True, average_stack=True):
    # measure the shifts
    return_dict = register_rigid_translate_pyramid(image, pyramid_size, align_stack or average_stack)

    if crop_stack and (align_stack or average_stack):

        aligned_stack = return_dict['aligned_stack']
        cum_shifts = return_dict['cumulative_shifts']

        # get min and max shifts
        mn = cum_shifts.min(axis=0)
        mx = cum_shifts.max(axis=0)

        # round properly (to largest absolute value)
        mn = np.multiply(np.rint(mn), np.sign(mn)).astype(int)
        mx = np.multiply(np.rint(mx), np.sign(mx)).astype(int)

        sx = aligned_stack.shape[1]
        sy = aligned_stack.shape[0]

        return_dict['aligned_stack'] = aligned_stack[mx[0]:sx-mn[0], mx[1]:sy-mn[1], :]

    if average_stack:
        return_dict['averaged_stack'] = np.mean(return_dict['aligned_stack'], axis=2)

    return return_dict


def register_rigid_translate_pyramid(stack, pyramid_size=3, align_stack=True):
    sz = stack.shape[2]

    cumulative_shifts = np.zeros((sz, 2))

    if align_stack:
        aligned = np.zeros_like(stack)
        aligned[:, :, 0] = stack[:, :, 0]

    i = 1
    pyramid_counter = 0
    while i < sz:
        reference = stack[:, :, pyramid_counter*pyramid_size]

        cumulative_shifts[i, :] = -1 * cross_correlate(stack[:, :, i], reference)

        cumulative_shifts[i, :] += cumulative_shifts[pyramid_counter*pyramid_size, :]

        if align_stack:
            aligned[:, :, i] = interpolate_shift(stack[:, :, i], cumulative_shifts[i, :])

        if i % pyramid_size == 0:
            pyramid_counter += 1
        i += 1

    outputs = {'cumulative_shifts': cumulative_shifts}

    if align_stack:
        outputs['aligned_stack'] = aligned

    return outputs

