import numpy as np

from GUI.Controls.Plot.Plottables import HistogramPlot
from GUI.Utilities.enums import AnnotationType
from GUI.Controls.Plot.Techniques import OglQuadrilateralTechnique


class PolarHistogramPlot(HistogramPlot):
    def __init__(self, bin_edges, frequency, min_r=0.0, max_r=1.0, mid=np.zeros((2, )), fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), border_width=2,
                 z_value=1, visible=True):

        super(PolarHistogramPlot, self).__init__(None, None,
                                                 fill_colour=fill_colour,
                                                 border_colour=border_colour,
                                                 border_width=border_width,
                                                 z_value=z_value,
                                                 visible=visible)

        self.plot_type = AnnotationType.PolarHistogram

        self.min_r = min_r
        self.max_r = max_r
        self.mid = mid

        if bin_edges is not None and frequency is not None:
            self.set_data(bin_edges, frequency)

    def p_to_c(self, radius, theta):
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        p = np.array([x, y])
        return p + self.mid

    @property
    def limits(self):
        return np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float32)

    def set_data(self, edges, frequency):
        # this is where we make the difference
        # use our x,y as polar and convert to cartesian

        # first convert our bin edges to be in the range 0 to 2pi
        edges = edges - edges[0]
        edges = 2 * np.pi * edges / edges[-1]

        # now our frequency values edges in the range 0-1 (for now as a start)
        # assume frequency starts at 0
        if frequency.max() > 0:
            frequency = frequency - frequency.min()
            frequency = frequency / frequency.max()
            frequency = frequency * (self.max_r - self.min_r) + self.min_r

        # get number of bins for convenience
        n_bins = edges.size - 1

        #
        # set up the bar (aka the fill) of the histogram
        #

        self.bars = []
        for i in range(n_bins):
            rect = OglQuadrilateralTechnique(fill_colour=self.fill_colour / 255,
                                             border_colour=np.zeros((4, )),
                                             border_width=0, z_value=self.z_value, visible=self.visible)
            rect.parent = self._parent
            rect.initialise()

            t1 = edges[i]
            t2 = edges[i+1]

            r1 = self.min_r
            r2 = frequency[i]

            p1 = self.p_to_c(r1, t1)
            p2 = self.p_to_c(r2, t1)
            p3 = self.p_to_c(r2, t2)
            p4 = self.p_to_c(r1, t2)

            # p1 = (p1 + 1) / 2
            # p2 = (p2 + 1) / 2
            # p3 = (p3 + 1) / 2
            # p4 = (p4 + 1) / 2

            rect.make_buffers(p1, p2, p3, p4)
            self.bars.append(rect)

        #
        # Set the histogram outline, this is ever so slightly more complicated
        #

        # 2 points per bin, plus edge points
        n_border_points = n_bins * 2 + 2
        # line points are in yx format
        border_points = np.zeros((n_border_points, 2), dtype=np.float32)

        # all the ::-1 as this is yx and before was xy... sigh
        border_points[0, ::-1] = self.p_to_c(frequency[0], edges[0])
        border_points[-1, ::-1] = self.p_to_c(frequency[0], edges[-1])

        for i in range(n_bins):
            f = frequency[i]
            left_edge = edges[i]
            right_edge = edges[i+1]
            border_points[i * 2 + 1, ::-1] = self.p_to_c(f, left_edge)
            border_points[i * 2 + 2, ::-1] = self.p_to_c(f, right_edge)

        self.outline.make_buffers(border_points)

        try:
            self.initialise()
        except Exception as e:
            return