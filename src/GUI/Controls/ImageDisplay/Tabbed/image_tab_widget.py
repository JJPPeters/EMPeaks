from PyQt5 import QtWidgets


class ImageTabWidget(QtWidgets.QTabWidget):
    def __init__(self, main_window, parent=None):
        super(ImageTabWidget, self).__init__(parent)

        self.main_window = main_window

        self.currentChanged.connect(self.set_tab_as_active)

        self.tabCloseRequested.connect(self.close_tab)

    def set_tab_as_active(self, index):
        if index == -1:
            id = None
        else:
            id = self.widget(index).id

        self.main_window.last_active = id

    def close_tab(self, index):
        id = self.widget(index).id
        self.main_window.remove_image(id)
        self.removeTab(index)
