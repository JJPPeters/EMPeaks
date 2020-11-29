from PyQt5 import QtCore, QtGui, QtWidgets
from .colour_map_direction_item import ColMapDirectionItem
from .slider_control_widget import SlideControlWidget


class DirectionControlWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(DirectionControlWidget, self).__init__(parent)

        # start off with a boring vertical layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        # self.verticalLayout.setSpacing(0)
        # self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # create the histogram widget
        self.wheel = ColMapDirectionItem()
        self.wheel.setFixedWidth(175)
        self.wheel.setFixedHeight(175)

        # variable for the angle, this gets reset basically on creating the slider
        self.Angle = 0

        # these are our default values, they will be changed very quickly by the slider signals when they
        # are created
        self.B = 0.5
        self.C = 0.5
        self.G = 0.5

        # create slider widgets
        self.slider_brightness = SlideControlWidget(self, name="Brightness", min=0, max=100, default=50, scale=0.01)
        self.slider_contrast = SlideControlWidget(self, name="Contrast", min=0, max=100, default=50, scale=0.01)
        self.slider_gamma = SlideControlWidget(self, name="Gamma", min=0, max=100, default=50, scale=0.01)

        # create slider widgets
        self.slider_angle = SlideControlWidget(self, name="Angle", min=0, max=360, default=0, scale=1.)

        # add everything to the layout
        self.verticalLayout.addWidget(self.wheel)
        self.verticalLayout.addWidget(self.slider_angle)
        self.verticalLayout.addWidget(self.slider_brightness)
        self.verticalLayout.addWidget(self.slider_contrast)
        self.verticalLayout.addWidget(self.slider_gamma)

        # connect the sliders to the slots that update stuff :)
        self.slider_brightness.valueChanged.connect(self.brightnessChanged)
        self.slider_contrast.valueChanged.connect(self.contrastChanged)
        self.slider_gamma.valueChanged.connect(self.gammaChanged)
        self.slider_angle.valueChanged.connect(self.angleChanged)

    def setImage(self, image):
        self.wheel.setImage(image)

        if image is None:
            return

        a_o = self.wheel.image.image_plot.angle_offset

        self.slider_angle.blockSignals(True)

        self.angleChanged(a_o, update=False)
        self.slider_angle.setVal(a_o * 100)

        self.slider_angle.blockSignals(False)

        self.wheel.updateAngle(self.Angle)

    # Slot
    def brightnessChanged(self, value, update=True):
        self.B = value
        if update:
            self.wheel.updateBCG(self.B, self.C, self.G)

    # Slot
    def contrastChanged(self, value, update=True):
        self.C = value
        if update:
            self.wheel.updateBCG(self.B, self.C, self.G)

    # Slot
    def gammaChanged(self, value, update=True):
        self.G = value
        if update:
            self.wheel.updateBCG(self.B, self.C, self.G)

    # Slot
    def angleChanged(self, value, update=True):
        self.Angle = value
        if update:
            self.wheel.updateAngle(self.Angle)

    def changeColmap(self, cmap):
        self.wheel.changeColmap(cmap)
        self.wheel.updateAngle(self.Angle)
