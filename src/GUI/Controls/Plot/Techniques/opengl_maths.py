import numpy as np


def translation_transform(x, y, z):
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 3] = x
    matrix[1, 3] = y
    matrix[2, 3] = z

    return matrix


def scale_transform(x, y, z):
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 0] = x
    matrix[1, 1] = y
    matrix[2, 2] = z

    return matrix


def orthographic_projection(t, l, b, r):
    matrix = np.identity(4, dtype=np.float32)
    matrix[0, 0] = 2 / (r - l)
    matrix[1, 1] = 2 / (t - b)

    matrix[0, 3] = -1 * (r + l) / (r - l)
    matrix[1, 3] = -1 * (t + b) / (t - b)

    n = 1
    f = 1000

    matrix[2, 2] = -2 / (f - n)
    matrix[2, 3] = -(f + n) / (f - n)

    return matrix

def rotation_transform(rotation_x, rotation_y, rotation_z, centre_x=0.0, centre_y=0.0, centre_z=0.0):
    r_x = np.radians(rotation_x)
    r_y = np.radians(rotation_y)
    r_z = np.radians(rotation_z)

    x_matrix = np.identity(4, dtype=np.float32)
    x_matrix[1, 1] = np.cos(r_x)
    x_matrix[2, 2] = np.cos(r_x)

    x_matrix[1, 2] = -np.sin(r_x)
    x_matrix[2, 1] = np.sin(r_x)

    y_matrix = np.identity(4, dtype=np.float32)
    y_matrix[0, 0] = np.cos(r_y)
    y_matrix[2, 2] = np.cos(r_y)

    y_matrix[0, 2] = np.sin(r_y)
    y_matrix[2, 0] = -np.sin(r_y)

    z_matrix = np.identity(4, dtype=np.float32)
    z_matrix[0, 0] = np.cos(r_z)
    z_matrix[1, 1] = np.cos(r_z)

    z_matrix[0, 1] = -np.sin(r_z)
    z_matrix[1, 0] = np.sin(r_z)

    matrix = x_matrix @ y_matrix @ z_matrix

    if centre_x != 0.0 or centre_y != 0.0 or centre_z != 0.0:
        shift = translation_transform(centre_x, centre_y, centre_z)
        unshift = translation_transform(centre_x, centre_y, centre_z)

        return unshift @ (matrix @ shift)

    return matrix

def camera_transform(target, up):
    n = target / np.linalg.norm(target)
    u = up / np.linalg.norm(up)
    v = np.cross(n, u)

    matrix = np.identity(4, dtype=np.float32)
    matrix[0, :3] = u
    matrix[2, :3] = v
    matrix[3, :3] = n

    return matrix
