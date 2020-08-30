import numpy as np
import math
from scipy.spatial.distance import cdist


def get_point_distance(x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def cartesian_to_polar(y, x, deg=False):
    mag = np.hypot(y, x)
    ang = np.angle(x + 1j * y, deg=deg)
    if deg:
        ang = ang % 360
    else:
        ang = ang % (2 * np.pi)

    return mag, ang


def get_nearest_neighbours(points, reference, neighbours):
    try:
        # if from this you wanted to get the centre of mass of the nearest atoms, just use
        # centre = np.mean(reference[inds], axis=1)

        dist = cdist(points, reference, 'Euclidean')

        # todo: could make this an option? (it's not hard to work our that a point is 0.0 from itself though...)
        # to remove self from consideration, just set the diagonal to infinity
        # we could remove these elements, but it fucks up the indexing
        if np.array_equal(points, reference):
            np.fill_diagonal(dist, np.inf)

        inds = np.argpartition(dist, neighbours)[:, :neighbours]

        # for funny indexing see: https://stackoverflow.com/a/20104162
        return reference[inds], inds, dist[np.arange(inds.shape[0])[:, None], inds]
    except MemoryError:
        return get_nearest_neighbour_large(points, reference, neighbours)


def get_nearest_neighbour_large(points, reference, neighbours):
    # if from this you wanted to get the centre of mass of the nearest atoms, just use
    # centre = np.mean(reference[inds], axis=1)
    inds = np.zeros((points.shape[0], neighbours), dtype=np.int)
    for i in range(points.shape[0]):
        dist = cdist(np.array([points[i]]), reference, 'Euclidean')

        inds[i] = np.argpartition(dist, neighbours)[:, :neighbours]

    return reference[inds], inds, dist[np.arange(inds.shape[0])[:, None], inds]


def distance_2d(x1, y1, x2, y2):
    return np.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))


def point_in_rect(p, top, left, bottom, right):
    return right > p[0] > left and top > p[1] > bottom


def point_array_in_rect(p_array, t, l, b, r):
    return np.logical_and(p_array[:, 1] <= r, np.logical_and(p_array[:, 1] >= l, np.logical_and(p_array[:, 0] <= t, p_array[:, 0] >= b)))


def point_in_poly(p, poly):
    n = poly.shape[0]
    poly = poly[ccw_argsort(poly)]
    inside = False
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if min(p1y, p2y) < p[1] <= max(p1y, p2y):
            if p[0] <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (p[1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or p[0] <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def ccw_argsort(a):
    b = a - np.mean(a, 0)
    return np.argsort(np.arctan2(b[:, 0], b[:, 1]))


def fit_3_point_parabola(data, limit=1):
    x1 = -1
    x2 = 0
    x3 = 1

    y1 = data[0].astype(np.float64)
    y2 = data[1].astype(np.float64)
    y3 = data[2].astype(np.float64)

    denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
    if denom == 0:
        return 0

    A = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
    B = (x3*x3 * (y1 - y2) + x2*x2 * (y3 - y1) + x1*x1 * (y2 - y3)) / denom
    # C = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom

    if A == 0:
        return 0

    offset = -B / (2*A)

    if offset > limit or offset < -limit:
        return 0
    else:
        return offset


def affine_transform_points(points, b, affb):
    Affu = np.array([[0, affb[0, 0], affb[1, 0]], [0, affb[0, 1], affb[1, 1]]])
    Imu = np.array([[1, 1, 1], [b[0, 0], b[1, 0], b[2, 0]], [
                   b[0, 1], b[1, 1], b[2, 1]]])
    AffT = Affu.dot(np.linalg.inv(Imu))
    sz = points.shape[0]
    Mm = np.column_stack((np.ones((sz, 1)), points[:, 0],
                          points[:, 1]))
    output = np.einsum('ji,ki->kj', AffT, Mm)

    return output
