from PyQt5 import QtWidgets, QtCore
from collections import OrderedDict
from typing import Union
import numpy as np

from GUI.Controls.Plot import PlotWidget
from GUI.Controls.Plot.Plottables import ImagePlot, ScatterPlot, PolarImagePlot, QuiverPlot
from GUI.Utilities.enums import ImageType, WindowType, ComplexDisplay, AnnotationType


class ImageDisplayWidget(QtWidgets.QWidget):
    sigClickedCoords = QtCore.pyqtSignal(object)
    sigPlottablesChanged = QtCore.pyqtSignal(object)
    sigImageChanged = QtCore.pyqtSignal(object)

    def __init__(self, image_name, window_id, main_win, modal=False, complex_type=ComplexDisplay.Real):

        super(ImageDisplayWidget, self).__init__()

        # this is the main window reference
        self.main_win = main_win

        # this is used to set the histogram display correctly
        self.windowType = WindowType.Image
        # this is a list of everything we have to plot
        self.plottables = OrderedDict()
        # this id is more of a user facing id, to help them identify images
        self.id = window_id
        # this is the title of the image (e.g. the filename)
        self.name = image_name


        #
        # UI
        #
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.plot_item = PlotWidget(show_axes=False)

        self.layout.addWidget(self.plot_item, 0, 1)

        self.setLayout(self.layout)
        #
        #
        #

        # self.plot_item.plot_view.signal_mouse_moved.connect(self.update_cursor)

        self.plot_item.plot_view.signal_rect_selected.connect(self.select_from_rect)
        self.plot_item.plot_view.signal_mouse_clicked.connect(self.select_from_click)

    @property
    def image_plot(self) -> Union[ImagePlot, None]:
        if 'Image' in self.plottables.keys():
            return self.plottables['Image']
        return None

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

    def delete_plottable(self, tag, update=True):
        if tag not in self.plottables:
            return

        tagType = self.plottables[tag].plot_type

        i = None

        if tagType == AnnotationType.Scatter:
            i = self.ui.plot.plot_view.remove_widget(self.plottables[tag])
            del self.plottables[tag]

        if tagType == AnnotationType.Quiver:
            i = self.ui.plot.plot_view.remove_widget(self.plottables[tag])
            del self.plottables[tag]

        if tagType == AnnotationType.Basis:
            i = self.ui.plot.plot_view.remove_widget(self.plottables[tag])
            del self.plottables[tag]

        self.ui.plot.update()

        if update:
            self.sigPlottablesChanged.emit(self)

        return i

    def hide_plottable(self, tag, visible):
        if tag not in self.plottables:
            raise Exception("Tried using annotation: " + tag + " but it doesnt exist")

        self.plottables[tag].visible = visible

        self.plot_item.update()

    def is_plottable_visible(self, tag):
        if tag not in self.plottables:
            return False

        visible = self.plottables[tag].visible

        return visible

    def click_add_point(self):
        tag = 'Peaks'
        # test if we have a scatter plot to add to (else create it)
        # or if our tag is not a scatter plot!
        if tag not in self.plottables.keys():
            self.add_plottable(tag, ScatterPlot(fill_colour=np.array(next(self.main_win.scatter_cols)) / 255, size=10, z_value=2))
        elif tag in self.plottables.keys() and not isinstance(self.plottables[tag], ScatterPlot):
            raise Exception("Trying to add points to non scatter plot")

        # connect the signal 'click' from the plot to the scatter
        self.plot_item.plot_view.signal_mouse_clicked.disconnect(self.select_from_click)
        self.plot_item.plot_view.signal_mouse_clicked.connect(self.add_point_from_click)

    def add_point_from_click(self, px, py, modifier, tag='Peaks'):

        self.plottables[tag].add_point(px, py)

        if modifier != QtCore.Qt.ShiftModifier:
            self.plot_item.plot_view.signal_mouse_clicked.disconnect(self.add_point_from_click)
            self.plot_item.plot_view.signal_mouse_clicked.connect(self.select_from_click)

    def select_from_click(self, px, py, modifier, tag='Peaks'):
        if tag in self.plottables.keys():
            self.plottables[tag].select_from_click(px, py)

    def select_from_rect(self, top, left, bottom, right, tag='Peaks'):
        if tag in self.plottables.keys():
            self.plottables[tag].select_in_rectangle(top, left, bottom, right)

    def delete_selected(self, tag='Peaks'):
        if tag in self.plottables.keys():
            self.plottables[tag].delete_selected()

            if self.plottables[tag].points.size == 0:
                self.delete_plottable(tag)
                self.ui.plot.update()
