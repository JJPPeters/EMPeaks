from PyQt5 import QtGui, QtWidgets
import numpy as np

from .gradient_item import GradientItem
from .histogram_view_box import HistogramViewBox

from Processing.Utilities import get_grid_sample_spacing, normalise_copy
from GUI.Controls.Plot.Plottables import HistogramPlot, LinePlot


class ColMapHistogramItem(QtWidgets.QWidget):

    def __init__(self, image=None, fillHistogram=True):
        super(ColMapHistogramItem, self).__init__()

        self.image = None
        self.currentXrange = None

        self.bins = 128

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # disabling the mouse should only disable the scroll...
        self.vb = HistogramViewBox()
        # self.vb.setBackgroundColor(QtGui.QColor(0, 0, 0, 0))

        self.gradient = GradientItem()
        self.gradient.setOrientation('horizontal')

        self.staticGradient = GradientItem()
        self.staticGradient.setOrientation('vertical')

        self.layout.addWidget(self.staticGradient, 0, 0)
        self.layout.addWidget(self.vb, 0, 1)
        self.layout.addWidget(self.gradient, 1, 1)

        # if not fillHistogram:
        #     fill_level = None
        # else:
        #     fill_level = 0.0

        self.plot = HistogramPlot(np.array([0.0, 1.0]), np.array([0]), fill_colour=np.array([147, 41, 132, 255]), border_width=0, border_colour=np.array([0, 0, 0, 0]), z_value=1, visible=True)

        self.origSample = np.linspace(0.0, 1.0, 100)
        self.sample = np.linspace(0.0, 1.0, 100)

        lpen = np.array([235, 235, 235, 255])

        self.BCplot = LinePlot(self.sample, self.sample, thickness=3, colour=lpen, z_value=2)
        self.Gplot = LinePlot(self.sample, self.sample, thickness=3, colour=lpen, z_value=2)

        self.vb.plot_view.add_widget(self.plot)
        self.vb.plot_view.add_widget(self.BCplot)
        self.vb.plot_view.add_widget(self.Gplot)

        self.vb.plot_view.fit_view()

        if image is not None:
            self.setImage(image)

        self.gradient.sigDoubleClick.connect(self.vb.rewindHistory)
        # self.gradient.sigGradientChanged.connect(self.gradientChanged)
        self.vb.sigLimitsChanged.connect(self.regionChanged)

    def setImage(self, img):
        self.image = img  # TODO: check that this just holds a reference, not a copy?
        if self.image is not None and self.image.image_plot is not None:
            # self.image.image_plot.set_colour_map(self.getLookupTable())

            if img.image_plot.colour_map is not None:
                self.changeColmap(img.image_plot.colour_map)
            else:
                raise Exception("Image does not have a colourmap defined")

            self.vb.axHistory = self.image.image_plot.limitsHistory
            self.applyHistogramHistory()

    def applyHistogramHistory(self):
        self.vb.makeCurrent()
        self.image.image_plot.limitsHistory = self.vb.axHistory  # update the limits history

        intens = self.image.image_plot.intensities

        target_sample_size = 5e5
        if intens.size < target_sample_size:
            hist_sample = intens
        else:
            sample_factor = int(np.sqrt(intens.size / target_sample_size))
            hist_sample = get_grid_sample_spacing(intens, sample_factor)

        r = np.array([np.min(hist_sample), np.max(hist_sample)])
        for h in self.image.image_plot.limitsHistory:
            h_range = np.array(h)

            r_r = r[1] - r[0]
            r[0] = r[0] + r_r * h_range[0]
            r[1] = r[1] - r_r * (1 - h_range[1])

        # TODO: maybe could include more data points to make sure histogram is more representative when zoomed in?

        trim_pcnt = 0.01
        sample_trimmed = hist_sample[np.logical_and(hist_sample >= r[0], hist_sample <= r[1])]
        p_low, p_high = np.percentile(sample_trimmed, (trim_pcnt, 100-trim_pcnt))

        r[0] = p_low
        r[1] = p_high

        self.currentXrange = np.zeros((3,), dtype=np.float32)
        self.currentXrange[0:2] = r
        self.currentXrange[2] = r[1] - r[0]

        hist = np.histogram(hist_sample, bins=self.bins, range=r)

        # I normalize this data so it is easier to verlay the plots!
        self.plot.set_data(normalise_copy(hist[1]), normalise_copy(hist[0]))
        self.vb.plot_view.fit_view()
        self.vb.update()

        self.image.image_plot.set_levels(r.astype(np.float32))

    def regionChanged(self):
        if self.image is not None and self.image.image_plot is not None:
            self.applyHistogramHistory()

    def updateBCG(self, B, C, G):
        self.vb.makeCurrent()
        if self.image is not None and self.image.image_plot is not None:
            self.image.image_plot.set_bcg(B, C, G)

        B = 1.5 - (B * 2)
        C = 5 ** (4 * (C - 0.5))
        G = 10 ** (4 * (-G + 0.5))

        self.gradient.updateBCG(B, C, G)

        # possible want to clip these to range?
        BCline = C*(self.origSample-B)+0.5
        Gline = self.origSample**G

        BCline = np.clip(BCline, 0.0, 1.0)
        Gline = np.clip(Gline, 0.0, 1.0)

        self.BCplot.set_points(self.sample, BCline)
        self.Gplot.set_points(self.sample, Gline)

        self.vb.update()

    def getLookupTable(self, img=None, n=None, alpha=True, original=False):
        if n is None:
            n = 256

        lut = self.gradient.getLookupTable(n, alpha=alpha, original=original)
        return lut

    def changeColmap(self, cmap):
        if self.image is not None and self.image.image_plot is not None:
            self.gradient.changeColmap(cmap)
            self.staticGradient.changeColmap(cmap)

            self.image.image_plot.set_colour_map(self.getLookupTable(original=True))

    def complexImageChanged(self, complex_type):
        if self.image is not None and self.image.image_plot is not None:
            self.image.image_plot.set_complex_type(complex_type)
            self.applyHistogramHistory()
            # TODO: reset the limits and the BCG (or leave them but they need to be applied)
