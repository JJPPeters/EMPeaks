from PyQt5 import QtCore, QtGui, QtWidgets

from GUI.Controls.Plot import PlotWidget


class ImageWindowUi(object):
    def setupUi(self, ImageWindow, filename):
        ImageWindow.setObjectName("ImageWindow")
        ImageWindow.resize(512, 512)
        ImageWindow.setMinimumSize(QtCore.QSize(500, 500))

        self.centralwidget = QtWidgets.QWidget(ImageWindow)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.imageItem = PlotWidget(show_axes=False)

        self.gridLayout.addWidget(self.imageItem, 0, 1)

        self.zScroll = QtWidgets.QScrollBar()
        self.zScroll.setOrientation(QtCore.Qt.Horizontal)
        self.zScroll.setVisible(False)

        self.gridLayout.addWidget(self.zScroll, 1, 1)

        ImageWindow.setCentralWidget(self.centralwidget)

        self.statusBar = QtWidgets.QStatusBar(ImageWindow)
        self.statusLabel = QtWidgets.QLabel(self.statusBar)
        self.statusLabel.setText("")
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.addWidget(self.statusLabel, 1)
        ImageWindow.setStatusBar(self.statusBar)

        ImageWindow.setWindowTitle(filename)
