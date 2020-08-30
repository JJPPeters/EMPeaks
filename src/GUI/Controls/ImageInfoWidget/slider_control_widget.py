from PyQt5 import QtCore, QtGui, QtWidgets
from .label_clickable import QLabelClickable

# A control that has a slider, shows a name and value label and cab be clicked to reset
class SlideControlWidget(QtWidgets.QWidget):

    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent, name="", min=0, max=100, default=50, scale=1.):
        super(SlideControlWidget, self).__init__(parent)

        # we will use this later to reset the values
        self.default = default
        self.scale = scale

        # create some layouts to use later
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.setObjectName("vbox")
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.setObjectName("hbox")
        
        # create a label to show the name
        self.lbl_name = QLabelClickable(self)
        self.lbl_name.setObjectName("lbl_name")
        
        # create a label to hold the value, requires a but more formatting
        self.lbl_val = QLabelClickable(self)
        self.lbl_val.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.lbl_val.setObjectName("lbl_val")

        # add widgets to the hbox and then the vbox
        self.hbox.addWidget(self.lbl_name)
        self.hbox.addWidget(self.lbl_val)
        self.vbox.addLayout(self.hbox)

        # create a slider, set the limits and default as desired
        # the current value will be set after connecting the signals
        self.slider = QtWidgets.QSlider(self)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")

        # add this to our layout!
        self.vbox.addWidget(self.slider)

        # set the text, the value label should be changed later anyway
        self.lbl_name.setText(name)
        self.lbl_val.setText("-")

        # connect up some slots
        self.lbl_name.sigDoubleClick.connect(self.resetVal)
        self.lbl_val.sigDoubleClick.connect(self.resetVal)
        QtCore.QMetaObject.connectSlotsByName(self)

        # IMPORTANT: needs to be set after the signals have been connected to make the label update when the widget
        # is created
        self.slider.setProperty("value", default)

    def resetVal(self):
        # only reset the value, this will cause the slider to emit it's value changed signal
        self.slider.setValue(self.default)

    def setVal(self, val):
        # only reset the value, this will cause the slider to emit it's value changed signal
        self.slider.setValue(val)

    def on_slider_valueChanged(self, value):
        val = value * self.scale
        self.lbl_val.setText("%.2f" % val)

        # emit out own signal, as we want the scaled value
        self.valueChanged.emit(val)
