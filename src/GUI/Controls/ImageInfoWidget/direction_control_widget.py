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
        self.wheel.updateAngle(self.Angle)

    # Slot
    def angleChanged(self, value):
        self.Angle = value
        self.wheel.updateAngle(self.Angle)

    def changeColmap(self, cmap):
        self.wheel.changeColmap(cmap)
        self.wheel.updateAngle(self.Angle)
