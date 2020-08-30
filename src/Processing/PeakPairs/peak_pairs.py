import numpy as np

from .peak_pairs_cython import peak_pair_c, sub_peak_pair_c
import scipy.spatial as spatial

from Processing.Utilities import affine_transform_points


# move to new folder/file?
def coord_to_index(peaks, inp):
    inp = inp.reshape((1, 2))

    tree = spatial.cKDTree(peaks)
    _, idx = tree.query(inp, k=1, p=2)

    return idx  # first one is a tuple


class PeakPair(object):

    def __init__(self, peaks, basis, affine_basis=np.array([[1, 0], [0, 1]]), thr=0.3):
        self.basis = basis  # store basis for future reference (i.e. for strain)
        self.affine_peaks = affine_transform_points(peaks, basis, affine_basis)
        # this is where the peak paris is done (for all peaks)
        self.pp_index_x = peak_pair_c(self.affine_peaks[:, 0], self.affine_peaks[:, 1],
                                affine_basis[0, 0], affine_basis[0, 1], thr)
        self.pp_index_y = peak_pair_c(self.affine_peaks[:, 0], self.affine_peaks[:, 1],
                                affine_basis[1, 0], affine_basis[1, 1], thr)


class SubPeakPair(PeakPair):

    def __init__(self, peaks, basis, sub_coords, affine_basis=np.array([[1, 0], [0, 1]]), thr=0.3):
        super(SubPeakPair, self).__init__(peaks, basis, affine_basis=affine_basis, thr=thr)

        self.subIndices = []

        for s in sub_coords:
            i = coord_to_index(peaks, s)

            sp = sub_peak_pair_c(self.pp_index_x[0], self.pp_index_x[1],
                                 self.pp_index_y[0], self.pp_index_y[1], i)

            self.subIndices.append(sp)
