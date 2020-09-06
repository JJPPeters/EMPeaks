from PyQt5 import QtGui, QtWidgets
import numpy as np

from .gradient_item import GradientItem
from .static_view_box import StaticViewBox
from GUI.Controls.Plot.Plottables import PolarImagePlot


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

        if image is not None:
            self.setImage(image)

        # Create the wheel image
        res = 256
        alpha = np.zeros((res, res), dtype=np.int8)
        xx, yy = np.mgrid[:res, :res]
        xx -= int(res / 2)
        yy -= int(res / 2)
        radius = np.square(xx) + np.square(yy)
        # divide by 2.5 is to give a bit of a border at the edge
        alpha[radius < np.square(res / 2.5)] = 1

        radius = radius.astype(np.float32)

        radius *= alpha
        radius /= np.amax(radius)

        # negative to get the right values (90 is up, 180 is left etc)
        angle = np.angle(-xx + 1j * yy, deg=False) - np.pi / 2
        angle[angle < 0] += 2*np.pi

        self.wheel = PolarImagePlot(angle, radius, alpha)
        self.wheel.set_colour_map(self.getLookupTable())
        self.vb.plot_view.add_widget(self.wheel)
        self.vb.plot_view.fit_view()

        self.gradient.sigGradientChanged.connect(self.gradientChanged)

    def setImage(self, img):
        self.image = img
        if img is not None:
            img.image_plot.set_colour_map(self.getLookupTable())

        self.lut = None

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
