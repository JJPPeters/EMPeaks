import numpy as np

from GUI.Controls.Plot.Techniques import OglQuadrilateralTechnique
from GUI.Utilities.enums import AnnotationType


class Rectangle(OglQuadrilateralTechnique):
    def __init__(self, limits=None, fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), border_width=2, z_value=1, visible=True):
        super(Rectangle, self).__init__(fill_colour=fill_colour,
                                        border_colour=border_colour,
                                        border_width=border_width,
                                        z_value=z_value,
                                        visible=visible)

        if limits is not None:
            self.set_data(limits[0], limits[1], limits[2], limits[3])

    @property
    def edges(self):
        return self.limits

    def set_data(self, t, l, b, r):
        # convert these limits to vertices

        p1 = np.array([l, b])
        p2 = np.array([r, b])
        p3 = np.array([l, t])
        p4 = np.array([r, t])

        self.make_buffers(p1, p2, p3, p4)
