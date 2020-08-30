import numpy as np


class LatticeBasis:
    def __init__(self, num_bases=1):
        self.num_bases = num_bases
        self.vector_coords = np.zeros((3, 2), dtype=np.float64)
        self.lattice_coords = np.zeros((num_bases, 2), dtype=np.float64)

    def get_basis_vectors(self):
        v1 = self.vector_coords[0, :] - self.vector_coords[1, :]
        v2 = self.vector_coords[0, :] - self.vector_coords[2, :]

        return v1, v2

    def set_from_coords_and_vectors(self, coords, a, b):
        self.lattice_coords = coords

        self.vector_coords[0, :] = self.lattice_coords[0, :]
        self.vector_coords[1, :] = self.lattice_coords[0, :] - a
        self.vector_coords[2, :] = self.lattice_coords[0, :] - b

    def get_largest_vector(self):
        # the largest vector is going to be one of the corners, so calculate them
        v1, v2 = self.get_basis_vectors()

        v3 = v1 + v2

        # get their magnitudes
        m1 = np.sqrt(np.sum(v1 ** 2))
        m2 = np.sqrt(np.sum(v2 ** 2))
        m3 = np.sqrt(np.sum(v3 ** 2))

        return np.max([m1, m2, m3])