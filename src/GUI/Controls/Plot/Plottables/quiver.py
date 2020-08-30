import numpy as np

from GUI.Controls.Plot.Techniques import OglQuiverTechnique

from Processing.Utilities import point_array_in_rect
from Processing.Utilities import get_point_distance
from GUI.Utilities.enums import AnnotationType


class QuiverPlot(OglQuiverTechnique):
    def __init__(self, pos=None, mag=None, ang=None, line_width=5, head_width=16, head_length=16, scale=1.0,
                 border_width=0.0, border_colour=np.array([1, 1, 1, 1]),
                 z_value=1, visible=True):
        super(QuiverPlot, self).__init__(line_width=line_width,
                                         head_width=head_width,
                                         head_length=head_length,
                                         scale=scale,
                                         border_width=border_width,
                                         border_colour=border_colour,
                                         z_value=z_value,
                                         visible=visible)

        self.plot_type = AnnotationType.Quiver

        self.parent = None

        self.positions = None
        self.magnitudes = None
        self.angles = None

        if pos is not None and mag is not None and ang is not None:
            self.set_data(pos, mag, ang)

    def set_data(self, positions, magnitudes, angles):
        self.positions = positions
        self.magnitudes = magnitudes
        self.angles = angles

        self.make_buffers(positions, magnitudes.reshape((-1, 1)), angles.reshape((-1, 1)))