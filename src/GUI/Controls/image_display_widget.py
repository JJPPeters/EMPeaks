from PyQt5 import QtWidgets, QtCore
from collections import OrderedDict
from typing import Union

from GUI.Controls.Plot import PlotWidget
from GUI.Controls.Plot.Plottables import ImagePlot, ScatterPlot, PolarImagePlot, QuiverPlot


class ImageDisplayWidget(QtWidgets.QWidget):
    sigClickedCoords = QtCore.pyqtSignal(object)
    sigPlottablesChanged = QtCore.pyqtSignal(object)
    sigImageChanged = QtCore.pyqtSignal(object)

    def __init__(self):  #, image_name, window_id, main_win=None, modal=False, complex_type=ComplexDisplay.Real):

        super(ImageDisplayWidget, self).__init__()

        # # this is the main window reference
        # self.main_win = main_win

        # this is a list of everything we have to plot
        self.plottables = OrderedDict()
        # # this id is more of a user facing id, to help them identify images
        # self.id = window_id
        # # this is the title of the image (e.g. the filename)
        # self.name = image_name

        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.plot_item = PlotWidget(show_axes=False)

        self.layout.addWidget(self.plot_item, 0, 1)

        self.setLayout(self.layout)

    # to type hint multiple types: https://stackoverflow.com/a/48709142
    def set_image_plot(self, image_plot: Union[ImagePlot, PolarImagePlot], keep_view=False):
        self.add_plottable('Image', image_plot, keep_view=keep_view)

        # if image_plot.slices > 1:
        #     self.ui.zScroll.setRange(0, image_plot.slices-1)
        #     self.ui.zScroll.valueChanged.connect(self.set_slice)
        #     self.ui.zScroll.setVisible(True)

        self.sigImageChanged.emit(self)

    def add_plottable(self, tag, entry, keep_view=True, update=True):
        if not self.isVisible():
            raise Exception("Must show window before plotting OpenGL elements")

        if tag in self.plottables:
            self.ui.plot.plot_view.remove_widget(self.plottables[tag])
        self.plottables[tag] = entry  # I think this destroys the old object!

        self.plot_item.plot_view.add_widget(self.plottables[tag], fit=not keep_view)
        if update:
            self.plot_item.update()

        self.sigPlottablesChanged.emit(self)
