from PyQt5 import QtGui, QtCore, QtWidgets

from GUI import MainWindow
from GUI.Controls.Plot.Plottables import ScatterPlot, ImagePlot

import numpy as np

from GUI.Utilities.enums import Console


class Module:
    _main_window = None

    def __init__(self):
        # self._main_window = None
        return

    def install(self):
        raise Warning("Module is designed to be overidden, cannot install bare module")

    def run(self):
        raise Warning("Module is designed to be overidden, cannot run bare module")

    @property
    def main_window(self):
        if self._main_window is not None:
            return self._main_window

        main_windows = [widget for widget in QtWidgets.QApplication.instance().topLevelWidgets()
                        if isinstance(widget, MainWindow)]

        if len(main_windows) == 1:
            self._main_window = main_windows[0]
        else:
            raise Warning("found incorrect number of main windows")

        return self._main_window

    @property
    def active_image_window(self):
        if self.main_window is not None:
            return self.main_window.last_active

    # TODO: get this to work when return size is different?
    def perform_on_image(self, func, update=True, keep_view=True):
        image = np.array(self.main_window.last_active.image_plot.image_data)

        if image.ndim == 2:
            image = func(image)
        elif image.ndim == 3:
            for i in range(image.shape[2]):
                image[:, :, i] = func(image[:, :, i])

        if update:
            self.create_or_update_image("Image", image, keep_view=True)

        return image

    def add_widget_to_image_window(self, widget, row, col):
        sz = self.active_image_window.normal_window_size
        w_sz = widget.size()
        w_sz.setHeight(0)
        sz += w_sz
        self.active_image_window.setNormalSize(sz)

        self.active_image_window.ui.gridLayout.addWidget(widget, row, col)
        widget.signal_result.connect(self.remove_widget_from_image_window)

    def remove_widget_from_image_window(self, widget, state):
        self.active_image_window.ui.gridLayout.removeWidget(widget)
        widget.close()
        sz = self.active_image_window.normal_window_size
        w_sz = widget.size()
        w_sz.setHeight(0)
        sz -= w_sz
        self.active_image_window.setNormalSize(sz)

    def set_colour_map(self, col_map_key):
        col_map = self.main_window.colour_maps[col_map_key]

        if self.main_window.image_requirements_met():
            self.main_window.ui.infoPanel.changeColMap(col_map)

    def set_console_message(self, message, message_type=Console.Message, show_id=True, bold=False,
                            end_new_line=True):

        self.main_window.set_console_message(message, message_type, self.active_image_window, show_id, bold, end_new_line)

    def create_or_update_image(self, tag, image, keep_view=True):
        if tag not in self.active_image_window.plottables:
            image_plot = ImagePlot(image)
            self.active_image_window.add_plottable(tag, image_plot, keep_view=keep_view)
        else:
            self.active_image_window.image_plot.set_data(image, keep_view=keep_view)

        self.active_image_window.sigImageChanged.emit(self.active_image_window)
        self.active_image_window.ui.imageItem.update()

    def create_or_update_scatter(self, tag, points):
        if tag not in self.active_image_window.plottables:
            scatter = ScatterPlot(points=points,
                                  size=10,
                                  fill_colour=np.array(next(self.main_window.scatter_cols)) / 255)
            self.active_image_window.add_plottable('Peaks', scatter)
        else:
            self.active_image_window.plottables[tag].set_points(points)

        self.active_image_window.ui.imageItem.update()
