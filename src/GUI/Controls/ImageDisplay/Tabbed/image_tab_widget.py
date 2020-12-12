from PyQt5 import QtWidgets


class ImageTabWidget(QtWidgets.QTabWidget):
    def __init__(self, main_window, parent=None):
        super(ImageTabWidget, self).__init__(parent)

        self.main_window = main_window

        self.currentChanged.connect(self.set_tab_as_active)

    def set_tab_as_active(self, i):
        id = self.currentWidget().id

        self.main_window.last_active = id
