import numpy as np

from Processing.Utilities import affine_transform_points
from Processing.PeakPairs import SubPeakPair
from Processing.PeakPairs import peak_pair_c

# TODO: cut down on a lot of repeated code (i.e. I should only need to peak pair the data once, and reuse that info)


def get_cell_lattice(lattice_peaks, peaks, basis, affine_basis=np.array([[1, 0], [0, 1]]), thr=0.3):
    affine_peaks = affine_transform_points(peaks, basis, affine_basis)

    # TODO: don't do this twice
    pp_1 = peak_pair_c(affine_peaks[:, 0], affine_peaks[:, 1], affine_basis[0, 0], affine_basis[0, 1], thr)
    pp_2 = peak_pair_c(affine_peaks[:, 0], affine_peaks[:, 1], affine_basis[1, 0], affine_basis[1, 1], thr)

    # TODO: convert lattice peaks to indices (or convert pp_1 to real values)

    # https://stackoverflow.com/questions/38674027/find-the-row-indexes-of-several-values-in-a-numpy-array
    # TODO: bit slow?
    lattice_peaks_ind = np.where((peaks == lattice_peaks[:, None]).all(-1))[1]

    cell_list = np.zeros((lattice_peaks.shape[0], 4), dtype=np.int)
    count = 0

    for p in lattice_peaks_ind:
        # find this peak in the peak part of our pairs lists
        pair_1 = np.where(p == pp_1[0])[0]
        pair_2 = np.where(p == pp_2[0])[0]

        # check we have the pairs we need
        # TODO: can I do anything to account and correct for multiple pairings?
        if pair_1.size != 1 or pair_2.size != 1:
            continue

        # get the actual pair values
        p_1 = pp_1[1][pair_1[0]]
        p_2 = pp_2[1][pair_2[0]]

        # now find the pairs of these new peaks
        # i know that the pair in the '1' direction must now be paired in the '2' direction (and vice versa)

        p_1_pair = np.where(p_1 == pp_2[0])[0]
        p_2_pair = np.where(p_2 == pp_1[0])[0]

        if p_1_pair.size != 1 or p_2_pair.size != 1:
            continue

        p_1_p = pp_2[1][p_1_pair[0]]
        p_2_p = pp_1[1][p_2_pair[0]]

        if p_1_p != p_2_p:  # the pairs don't form a loop
            continue

        # so now we know the indices of all our corners of the cell
        cell_list[count, 0] = p
        cell_list[count, 1] = p_1
        cell_list[count, 2] = p_2
        cell_list[count, 3] = p_1_p

        count += 1

    return np.delete(cell_list, np.arange(count, cell_list.shape[0]))
