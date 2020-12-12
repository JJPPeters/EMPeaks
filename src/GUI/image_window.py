from collections import OrderedDict

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from GUI.Utilities.enums import ImageType, WindowType, ComplexDisplay, AnnotationType
from GUI.Controls.Plot.Plottables import ImagePlot, ScatterPlot, PolarImagePlot, QuiverPlot
from GUI.UI.image_window_ui import ImageWindowUi
# import GUI.UI
from Processing.Utilities import point_array_in_rect
from Processing.Utilities import get_point_distance

from GUI.Controls.Plot.Techniques.opengl_image_technique import OglImageTechnique
from GUI.Controls.Plot.Techniques.opengl_polar_image_technique import OglPolarImageTechnique
from GUI.Controls.Plot.Techniques import OglScatterTechnique
from GUI.Controls.Plot.Techniques import OglQuiverTechnique

from typing import Union


class ImageWindow(QtWidgets.QMainWindow):

    sigClickedCoords = QtCore.pyqtSignal(object)
    sigPlottablesChanged = QtCore.pyqtSignal(object)
    sigImageChanged = QtCore.pyqtSignal(object)

    def __init__(self, image_name, window_id, master=None, modal=False, complex_type=ComplexDisplay.Real):
        # not sure I ever use this, but it cannot hurt
        if modal:
            super(ImageWindow, self).__init__(master, QtCore.Qt.Dialog)
        else:
            super(ImageWindow, self).__init__()

        self.windowType = WindowType.Image  # TODO: this might not be needed (just test class type)

        # these I am (more) confident about being useful
        self.master = master

        # this is a list of everything we have to plot
        self.plottables = OrderedDict()
        # this id is more of a user facing id, to help them identify images
        self.id = window_id
        # this is the title of the image (e.g. the filename)
        self.name = image_name

        # do the UI bits
        self.ui = ImageWindowUi()
        self.ui.setupUi(self, window_id + ': ' + image_name)
        self.setWindowIcon(master.windowIcon())

        # this is so we can resize the normal window size even when it is maximised
        self.normal_window_size = self.size()

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # self.ui.plot.plot_item.plot_view.signal_mouse_moved.connect(self.update_cursor)
        #
        # self.ui.plot.plot_item.plot_view.signal_rect_selected.connect(self.select_from_rect)
        # self.ui.plot.plot_item.plot_view.signal_mouse_clicked.connect(self.select_from_click)

    def event(self, event):
        # activate this window here
        # other windows activating should deactivate this one
        # not we still seem to need to handle this window closing
        if event.type() == QtCore.QEvent.WindowActivate:
            self.master.last_active = self
            # self.ui.imageItem.makeCurrent()
        # elif event.type() == QtCore.QEvent.WindowDeactivate:
        #     print("de-activate")

        return super(ImageWindow, self).event(event)

    # this mostly just makes the 'un-maximising' look less glitchy?
    # otherwise not needed
    def resizeEvent(self, event):
        if self.windowState() == QtCore.Qt.WindowMaximized:
            super(ImageWindow, self).resize(self.normal_window_size)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            if event.oldState() != QtCore.Qt.WindowNoState and self.windowState() == QtCore.Qt.WindowNoState:
                self.resize(self.normal_window_size)

    def setNormalSize(self, size: QtCore.QSize):
        self.normal_window_size = size
        if self.windowState() == QtCore.Qt.WindowNoState:
            self.resize(self.normal_window_size)

    def closeEvent(self, event):
        self.master.remove_image(self.id)

        self.deleteLater()  # If i call super closeEvent here i get sigsegv

    def keyPressEvent(self, evt):

        c_slice = self.image_plot.current_slice

        # want to delete a peak
        if evt.key() == QtCore.Qt.Key_Delete or evt.key() == QtCore.Qt.Key_Backspace:
            self.delete_selected()
        elif evt.key() == QtCore.Qt.Key_Left:
            self.ui.zScroll.setSliderPosition(c_slice - 1)
        elif evt.key() == QtCore.Qt.Key_Right:
            self.ui.zScroll.setSliderPosition(c_slice + 1)  # index is not from 0, hence the funny business





    def set_slice(self, index, update_slider=True):
        self.ui.plot.makeCurrent()
        self.image_plot.set_slice(index)



    # def update_cursor(self, px, py):
    #     if self.image_plot is None:
    #         return
    #
    #     intensity = None
    #     if isinstance(self.image_plot, PolarImagePlot):
    #         data = self.image_plot.angle_data
    #         intensity = self.image_plot.magnitude_data
    #     else:
    #         data = self.image_plot.image_data
    #
    #     sz = data.shape
    #     sy = sz[0] - 1
    #     sx = sz[1] - 1
    #
    #     xs = "%.2f" % px
    #     ys = "%.2f" % py
    #
    #     if data.ndim == 3:
    #         pos = (int(np.clip(py, 0, sy)), int(np.clip(px, 0, sx)), self.image_plot.current_slice)
    #     else:
    #         pos = int(np.clip(py, 0, sy)), int(np.clip(px, 0, sx))
    #
    #     if np.any(np.iscomplex(data)):
    #         ds = "%.2f + i%.2f" % (data[pos].real, data[pos].imag)
    #     else:
    #         ds = "%.2f" % data[pos]
    #
    #     if isinstance(self.image_plot, PolarImagePlot):
    #         if np.any(np.iscomplex(data)):
    #             ds += " (%.2f + i%.2f)" % (intensity[pos].real, intensity[pos].imag)
    #         else:
    #             ds += " (%.2f)" % intensity[pos]
    #
    #     # self.ui.statusLabel.setText("x, y: " + xs + ", " + ys + " = " + ds)
