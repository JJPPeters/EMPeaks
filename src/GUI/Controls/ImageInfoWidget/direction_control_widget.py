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

        # create slider widgets
        self.slider_angle = SlideControlWidget(self, name="Angle", min=0, max=360, default=0, scale=1.)

        # add everything to the layout
        self.verticalLayout.addWidget(self.wheel)
        self.verticalLayout.addWidget(self.slider_angle)

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
    def angleChanged(self, value, update=True):
        self.Angle = value
        if update:
            self.wheel.updateAngle(self.Angle)

    def changeColmap(self, cmap):
        self.wheel.changeColmap(cmap)
        self.wheel.updateAngle(self.Angle)
