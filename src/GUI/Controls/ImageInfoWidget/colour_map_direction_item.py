from PyQt5 import QtGui, QtWidgets
import numpy as np

from .gradient_item import GradientItem
from .static_view_box import StaticViewBox
from GUI.Controls.Plot.Plottables import PolarImagePlot, PolarHistogramPlot
from Processing.Utilities import get_grid_sample_spacing, normalise_copy


class ColMapDirectionItem(QtWidgets.QWidget):

    def __init__(self, image=None, fillHistogram=True):
        super(ColMapDirectionItem, self).__init__()

        self.image = None
        self.lut = None

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.vb = StaticViewBox()
        # self.vb.setBackgroundColor(QtGui.QColor(0, 0, 0, 255))
        # self.vb.autoRange(padding=0.01)  # to get image ot fit later
        # self.vb.setAspectLocked(True)

        self.gradient = GradientItem()
        self.gradient.setOrientation('horizontal')

        self.layout.addWidget(self.vb, 0, 0)
        self.layout.addWidget(self.gradient, 1, 0)

        r = 128
        res = r * 2

        self.polar_hist = PolarHistogramPlot(np.array([0.0, 1.0]), np.array([0]), min_r=1.0, max_r=1.2, fill_colour=np.array([255, 255, 255, 200]),
                                  border_width=2, border_colour=np.array([255, 255, 255, 255]), z_value=1, visible=True)

        # Create the wheel image
        alpha = np.zeros((res, res), dtype=np.int8)
        xx, yy = np.mgrid[:res, :res]
        xx -= r
        yy -= r
        radius = np.square(xx) + np.square(yy)
        # divide by 2.5 is to give a bit of a border at the edge
        # alpha[radius < np.square(res / 2.5)] = 1
        alpha[radius < np.square(r)] = 1

        radius = radius.astype(np.float32)

        radius *= alpha
        radius /= np.amax(radius)

        # negative to get the right values (90 is up, 180 is left etc)
        angle = np.angle(-xx + 1j * yy, deg=False) - np.pi / 2
        angle[angle < 0] += 2*np.pi

        self.wheel = PolarImagePlot(angle, radius, alpha, pixel_scale=2 / res, origin=np.array([1.0, 1.0]))
        self.wheel.set_colour_map(self.getLookupTable())
        self.vb.plot_view.add_widget(self.wheel)
        self.vb.plot_view.add_widget(self.polar_hist)

        if image is not None:
            self.setImage(image)

        self.gradient.sigGradientChanged.connect(self.gradientChanged)

    def setImage(self, img):
        self.image = img
        if img is not None and img.image_plot is not None:
            # TODO: orignally this as here. very odd
            # img.image_plot.set_colour_map(self.getLookupTable())

            if img.image_plot.colour_map is not None:
                self.changeColmap(img.image_plot.colour_map)

            self.set_angle_histogram()

        self.vb.plot_view.fit_view_to(np.array([1.2, -1.2, -1.2, 1.2]))

        self.lut = None

    def set_angle_histogram(self):

        intens = self.image.image_plot.angle_data

        target_sample_size = 5e5
        if intens.size < target_sample_size:
            hist_sample = intens
        else:
            sample_factor = int(np.sqrt(intens.size / target_sample_size))
            hist_sample = get_grid_sample_spacing(intens, sample_factor)

        hist = np.histogram(hist_sample, bins=180, range=(0, 2 * np.pi))

        self.polar_hist.set_data(normalise_copy(hist[1]), normalise_copy(hist[0]))

    def gradientChanged(self):
        # if self.image is not None:
        #     # send function pointer, not the result
        #     self.image.image_plot.set_colour_map(self.getLookupTable())
        #
        # self.lut = None
        # # self.sigLookupTableChanged.emit(self)
        return

    def getLookupTable(self, img=None, n=None, alpha=True, original=False):
        if n is None:
            n = 256

        if self.lut is None:
            self.lut = self.gradient.getLookupTable(n, alpha=alpha, original=True)
        return self.lut

    def changeColmap(self, cmap):
        if self.image is not None:
            self.gradient.changeColmap(cmap)
            self.wheel.set_colour_map(self.getLookupTable())

            self.image.image_plot.set_colour_map(self.getLookupTable(original=True))

        self.lut = None

    def updateAngle(self, Angle):
        if self.image is not None and self.image.image_plot is not None:
            self.image.image_plot.set_cmap_angle_offset(Angle)

        self.gradient.updateAngle(Angle)
        self.wheel.set_cmap_angle_offset(Angle)
