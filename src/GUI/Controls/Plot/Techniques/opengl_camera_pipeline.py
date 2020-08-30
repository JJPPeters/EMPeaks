import numpy as np
from .opengl_maths import *


class OglCameraPipeline:
    def __init__(self, invert_y=False):

        self.invert_y = invert_y

        # the projection transformation parameters
        self.projection_edges = np.array([100, -100, -100, 100], dtype=np.float32)

    @property
    def yf(self):
        if self.invert_y:
            return -1
        else:
            return 1

    def get_projection_matrix(self):
        if self.invert_y:
            projection = orthographic_projection(self.projection_edges[0],
                                                 self.projection_edges[1],
                                                 self.projection_edges[2],
                                                 self.projection_edges[3])
        else:
            projection = orthographic_projection(self.projection_edges[2],
                                                 self.projection_edges[1],
                                                 self.projection_edges[0],
                                                 self.projection_edges[3])

        return projection

    def set_projection_limits(self, t, l, b, r):
        self.projection_edges[0] = t
        self.projection_edges[1] = l
        self.projection_edges[2] = b
        self.projection_edges[3] = r
