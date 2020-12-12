from PyQt5 import QtCore, QtGui, QtWidgets

from GUI.Controls.Plot import PlotWidget
from GUI.Controls.ImageDisplay import ImageDisplayWidget


class ImageWindowUi(object):
    def setupUi(self, image_window, filename):
        image_window.resize(512, 512)
        image_window.setMinimumSize(QtCore.QSize(500, 500))

        # self.central_widget = QtWidgets.QWidget(image_window)

        # self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        # self.gridLayout.setSpacing(2)
        # self.gridLayout.setContentsMargins(0, 0, 0, 0)
        #
        # self.imageItem = PlotWidget(show_axes=False)
        #
        # self.gridLayout.addWidget(self.imageItem, 0, 1)
        #
        # self.zScroll = QtWidgets.QScrollBar()
        # self.zScroll.setOrientation(QtCore.Qt.Horizontal)
        # self.zScroll.setVisible(False)
        #
        # self.gridLayout.addWidget(self.zScroll, 1, 1)
        #
        # ImageWindow.setCentralWidget(self.centralwidget)
        #
        # self.statusBar = QtWidgets.QStatusBar(ImageWindow)
        # self.statusLabel = QtWidgets.QLabel(self.statusBar)
        # self.statusLabel.setText("")
        # self.statusBar.setSizeGripEnabled(False)
        # self.statusBar.addWidget(self.statusLabel, 1)
        # ImageWindow.setStatusBar(self.statusBar)
        #
        # ImageWindow.setWindowTitle(filename)

        self.plot = ImageDisplayWidget()

        image_window.setCentralWidget(self.plot)