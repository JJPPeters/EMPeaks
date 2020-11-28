import numpy as np

from GUI.Controls.Plot.Techniques import OglLineTechnique
from GUI.Controls.Plot.Plottables import Rectangle
from PyQt5.QtWidgets import QOpenGLWidget
from GUI.Utilities.enums import AnnotationType

class HistogramPlot:
    def __init__(self, bin_edges, frequency, fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), border_width=2,
                 z_value=1, visible=True):

        self.plot_type = AnnotationType.Histogram

        self._parent = None

        self.z_value = z_value
        self.visible = visible

        self.fill_colour = fill_colour
        self.border_width = border_width
        self.border_colour = border_colour

        # rect = OglRectangleTechnique(fill_colour=self.fill_colour / 255,
        #                              border_colour=np.zeros((4,)),
        #                              border_width=0, z_value=self.z_value, visible=self.visible)

        self.outline = OglLineTechnique(thickness=self.border_width, colour=self.border_colour / 255,
                                        z_value=self.z_value, visible=self.visible)

        self.bars = []
        # self.outline = None

        if bin_edges is not None and frequency is not None:
            self.set_data(bin_edges, frequency)

    @property
    def parent(self: QOpenGLWidget):
        return self._parent

    @parent.setter
    def parent(self, p: QOpenGLWidget):
        self._parent = p
        self.outline.parent = p
        for r in self.bars:
            r.parent = p

    @property
    def limits(self):
        return self.outline.limits

    def initialise(self):
        for bar in self.bars:
            bar.initialise()

        self.outline.initialise()

    def on_click(self, dud1, dud2, dud3):
        return

    def set_data(self, edges, frequency):
        # get number of bins for convenience
        n_bins = edges.size - 1

        #
        # set up the bar (aka the fill) of the histogram
        #

        self.bars = []
        for i in range(n_bins):
            rect_edges = [frequency[i], edges[i], 0.0, edges[i+1]]
            rect = Rectangle(limits=rect_edges, fill_colour=self.fill_colour / 255,
                             border_colour=np.zeros((4, )),
                             border_width=0, z_value=self.z_value, visible=self.visible)
            rect.parent = self._parent  # important as these are created after the rest of this has been initialised
            self.bars.append(rect)

        # self.outline = OglLineTechnique(thickness=self.border_width, colour=self.border_colour / 255,
        #                                 z_value=self.z_value, visible=self.visible)

        #
        # Set the histogram outline, this is ever so slightly more complicated
        #

        # 2 points per bin, plus edge points
        n_border_points = n_bins * 2 + 2
        # line points are in yx format
        border_points = np.zeros((n_border_points, 2), dtype=np.float32)

        border_points[0, 1] = edges[0]
        border_points[-1, 1] = edges[-1]

        for i in range(n_bins):
            f = frequency[i]
            left_edge = edges[i]
            right_edge = edges[i+1]
            border_points[i * 2 + 1, 0] = f
            border_points[i * 2 + 2, 0] = f
            border_points[i * 2 + 1, 1] = left_edge
            border_points[i * 2 + 2, 1] = right_edge

        self.outline.make_buffers(border_points)

        try:
            self.initialise()
        except Exception as e:
            return

    def render(self, projection, width, height, ratio):
        for bar in self.bars:
            bar.render(projection, width, height, ratio)

        self.outline.render(projection, width, height, ratio)