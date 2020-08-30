import numpy as np
from scipy.ndimage.interpolation import map_coordinates


########################################################################################################################
# affine_transform
########################################################################################################################
# This transforms the image coordinates to the basis coordinates
#
# This is done by finding the corners of the affine transformed image, create array for the image coordinates covering
# this region, transforming them BACK to the original coordinates and using map_coordinates to get the intensities
def affine_transform(image, basis):
    # get the basis vectors from the basis coordinates
    v1 = basis[1, :] - basis[0, :]
    v2 = basis[2, :] - basis[0, :]

    # get the magnitude as we want to use this for the new basis (so magnitude will be preserved)
    mag1 = np.sqrt(v1[0] * v1[0] + v1[1] * v1[1])
    mag2 = np.sqrt(v2[0] * v2[0] + v2[1] * v2[1])

    # construct matrices representing the old (current) basis and the new one we want to map onto
    # TODO: set new_basis sensibly so this image undergoes minimal distortion/rotation
    new_basis = np.array([[mag1, 0], [0, mag2]])
    old_basis = np.array([[v1[0], v2[0]], [v1[1], v2[1]]])

    trans_matrix = new_basis.dot(np.linalg.inv(old_basis))

    in_shp = np.array(image.shape)

    corners = np.zeros((4, 2))
    corners[1] = [in_shp[0], 0]
    corners[2] = [in_shp[0], in_shp[1]]
    corners[3] = [0, in_shp[1]]

    corners = trans_matrix.dot(corners.T).T

    min_x = np.floor(np.min(corners[:, 1])).astype(np.int)
    max_x = np.ceil(np.max(corners[:, 1])).astype(np.int)
    min_y = np.floor(np.min(corners[:, 0])).astype(np.int)
    max_y = np.ceil(np.max(corners[:, 0])).astype(np.int)

    w = max_x - min_x
    h = max_y - min_y

    y, x = np.mgrid[min_y:max_y, min_x:max_x]

    yx = np.hstack((y.reshape(-1, 1), x.reshape(-1, 1)))
    yx = np.linalg.inv(trans_matrix).dot(yx.T)  # not transposed back for input to map_coordinates

    return map_coordinates(image, yx, order=3).reshape((h, w))
