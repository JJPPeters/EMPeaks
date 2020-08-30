import os, sys
from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets
import prog_info as Program


class SplashWindow(QtWidgets.QMainWindow):
    def __init__(self, application_path):
        screen_id = QtWidgets.QApplication.desktop().screenNumber()
        screen = QtWidgets.QApplication.desktop().screen(screen_id)
        px_ratio = screen.devicePixelRatio()

        qs = QtCore.QSize(512, 297)

        svg_file_name = os.path.join(application_path, Program.Splash)
        renderer = QtSvg.QSvgRenderer(svg_file_name)
        pm = QtGui.QPixmap(px_ratio * qs)
        pm.fill(QtGui.QColor(255, 255, 122, 125))
        painter = QtGui.QPainter()

        painter.begin(pm)
        renderer.render(painter)
        painter.end()

        pm.setDevicePixelRatio(px_ratio)

        super(SplashWindow, self).__init__()

        self.setWindowFlags(QtCore.Qt.SplashScreen)
        self.setFixedSize(qs)

        lbl = QtWidgets.QLabel(parent=self)
        lbl.setPixmap(pm)

        self.setCentralWidget(lbl)

        self.title_label = QtWidgets.QLabel(parent=self)
        self.title_label.setStyleSheet("color: #FAFAFA; font: 40pt \"Roboto\"")
        self.title_label.setText(Program.Name)
        self.title_label.setGeometry(20, 100, 472, 80)

        self.version_label = QtWidgets.QLabel(parent=self)
        self.version_label.setStyleSheet("color: #FAFAFA; font: 10pt \"Roboto\"")
        self.version_label.setText(Program.Version)
        self.version_label.setGeometry(20, 135, 472, 80)

        self.message_label = QtWidgets.QLabel(parent=self)
        self.message_label.setStyleSheet("color: #FAFAFA; font: 10pt \"Roboto\"")
        self.message_label.setText("Loading...")
        self.message_label.setGeometry(20, 200, 472, 80)

    def showMessage(self, message: str) -> None:
        self.message_label.setText(message)
        QtWidgets.QApplication.processEvents()