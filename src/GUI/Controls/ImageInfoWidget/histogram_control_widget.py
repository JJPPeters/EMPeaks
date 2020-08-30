from PyQt5 import QtCore, QtGui, QtWidgets
from .colour_map_histogram_item import ColMapHistogramItem
from .slider_control_widget import SlideControlWidget


class HistogramControlWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(HistogramControlWidget, self).__init__(parent)

        # start off with a boring vertical layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        # self.verticalLayout.setSpacing(0)
        # self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # create the histogram widget
        self.bar = ColMapHistogramItem()
        self.bar.setFixedWidth(175)
        self.bar.setFixedHeight(175)

        # these are our default values, they will be changed very quickly by the slider signals when they
        # are created
        self.B = 0.5
        self.C = 0.5
        self.G = 0.5

        # create slider widgets
        self.slider_brightness = SlideControlWidget(self, name="Brightness", min=0, max=100, default=50, scale=0.01)
        self.slider_contrast = SlideControlWidget(self, name="Contrast", min=0, max=100, default=50, scale=0.01)
        self.slider_gamma = SlideControlWidget(self, name="Gamma", min=0, max=100, default=50, scale=0.01)

        self.combo_complex = QtWidgets.QComboBox(self)
        self.combo_complex.addItems(["Real", "Imaginary", "Amplitude", "Phase", "Power spectrum"])
        # self.combo_complex.setVisible(False)

        # add everything to the layout
        self.verticalLayout.addWidget(self.bar)

        self.verticalLayout.addWidget(self.combo_complex)

        self.verticalLayout.addWidget(self.slider_brightness)
        self.verticalLayout.addWidget(self.slider_contrast)
        self.verticalLayout.addWidget(self.slider_gamma)

        # connect the sliders to the slots that update stuff :)
        self.slider_brightness.valueChanged.connect(self.brightnessChanged)
        self.slider_contrast.valueChanged.connect(self.contrastChanged)
        self.slider_gamma.valueChanged.connect(self.gammaChanged)
        self.combo_complex.currentIndexChanged.connect(self.complexDisplayChanged)

    def setImage(self, image):
        self.bar.setImage(image)

        if image is None:
            return

        bcg = self.bar.image.image_plot.BCG

        self.slider_brightness.setVal(bcg[0]*100)
        self.slider_contrast.setVal(bcg[1]*100)
        self.slider_gamma.setVal(bcg[2]*100)

        # force this or it doesnt update the values properly (and ends up applying them between images)
        self.bar.updateBCG(self.B, self.C, self.G)

        # handle the complex part
        cd = self.bar.image.image_plot.complex_display
        if cd is not None:
            self.combo_complex.setCurrentIndex(cd)

        self.combo_complex.setVisible(self.bar.image.image_plot.is_complex)

    # Slot
    def brightnessChanged(self, value, update=True):
        self.B = value
        if update:
            self.bar.updateBCG(self.B, self.C, self.G)

    # Slot
    def contrastChanged(self, value, update=True):
        self.C = value
        if update:
            self.bar.updateBCG(self.B, self.C, self.G)

    # Slot
    def gammaChanged(self, value, update=True):
        self.G = value
        if update:
            self.bar.updateBCG(self.B, self.C, self.G)

    def changeColmap(self, cmap):
        self.bar.changeColmap(cmap)

    def setComplexDisplay(self, index):
        self.combo_complex.setCurrentIndex(index)

    def complexDisplayChanged(self, index):
        # emit a signal that updates the image?
        self.bar.complexImageChanged(index)
