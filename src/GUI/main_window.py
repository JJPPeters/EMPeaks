import os
import string
import sys
import traceback
from itertools import cycle

from PyQt5 import QtCore, QtGui, QtWidgets

import GUI
# from GUI import ImageWindow
from GUI.UI import MainWindowUi

from GUI.Controls.Plot.Plottables import ImagePlot

from GUI.Utilities import load_colour_maps, std_colour_maps
from GUI.Utilities.enums import Console


class MainWindow(QtWidgets.QMainWindow):
    lastActiveChanged = QtCore.pyqtSignal(object)

    def __init__(self, application_path, parent=None):
        super(MainWindow, self).__init__(parent)
        # set the exception hook so we can print exceptions
        self.default_except_hook = sys.excepthook
        sys.excepthook = self.show_exception

        self.modules = []

        self.children = {}
        self._last_active_id = None
        self.dialogGeom = None
        self.last_directory = os.path.expanduser("~")
        self.application_path = application_path

        # matplotlib colour scheme, minus the grey one (as images are defaulted to grey)
        # made them slightly transparent too
        self.scatter_cols = cycle([(31, 119, 180, 200),
                                   (255, 127, 14, 200),
                                   (44, 160, 44, 200),
                                   (214, 39, 40, 200),
                                   (148, 103, 189, 200),
                                   (140, 86, 75, 200),
                                   (227, 119, 194, 200),
                                   (188, 189, 34, 200),
                                   (23, 190, 207, 200)
                                   ])

        self.load_settings()
        self.colour_maps = load_colour_maps(application_path)

        self.ui = MainWindowUi(self, application_path)

        self.lastActiveChanged.connect(self.ui.infoPanel.showImageInfo)

    @property
    def last_active(self) -> GUI.ImageWindow:
        return self.children[self._last_active_id]

    @last_active.setter
    def last_active(self, new_id):
        if self._last_active_id == new_id:
            return

        if new_id not in self.children.keys():
            raise Exception(f"Cannot find child {new_id}")

        if self._last_active_id is not None:
            self.last_active.sigPlottablesChanged.disconnect()
            self.last_active.sigImageChanged.disconnect()
            self.ui.infoPanel.sigItemDeleted.disconnect()
            self.ui.infoPanel.sigItemHide.disconnect()

        self._last_active_id = new_id

        if self._last_active_id is not None:
            self.last_active.sigPlottablesChanged.connect(self.ui.infoPanel.updateItemList)
            self.last_active.sigImageChanged.connect(self.ui.infoPanel.updateImageHistogram)
            self.ui.infoPanel.sigItemDeleted.connect(self.last_active.delete_plottable)
            self.ui.infoPanel.sigItemHide.connect(self.last_active.hide_plottable)

        self.lastActiveChanged.emit(self.last_active)

    def image_requirements_met(self):
        return self.last_active is not None and isinstance(self.last_active, GUI.Controls.ImageDisplay.ImageDisplayWidget)

    def confirm_replace_peaks(self, tag):
        if tag in self.last_active.plottables:
            quit_msg = "This will override existing peaks"
            reply = QtWidgets.QMessageBox.question(self, 'Warning', quit_msg,
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
            return reply == QtWidgets.QMessageBox.Ok
        return True

    def generate_window_id(self):
        stop = False
        i = 1

        while not stop:
            pref = i
            key = ""
            while pref != 0:
                pref, let = divmod(pref, 27)
                key = string.ascii_uppercase[let - 1] + key

            if key not in self.children:
                return key
            i += 1

    def get_settings_path(self):
        if 'APPDATA' in os.environ:
            config_home = os.environ['APPDATA']
        elif 'XDG_CONFIG_HOME' in os.environ:
            config_home = os.environ['XDG_CONFIG_HOME']
        else:
            config_home = os.path.join(os.environ['HOME'], '.config')
        config_path = os.path.join(config_home, 'EMPeaks')
        if not os.path.exists(config_path):
            os.makedirs(config_path)

        setting_path = os.path.join(config_path, 'settings.user')

        return setting_path

    def load_settings(self):
        setting_path = self.get_settings_path()

        if os.path.isfile(setting_path):
            with open(setting_path, 'r') as f:
                directory = f.read()
                try:
                    if os.path.isdir(directory):
                        self.last_directory = directory
                except ValueError:
                    pass

    def save_settings(self, directory):
        setting_path = self.get_settings_path()

        if os.path.isdir(directory):
            self.last_directory = directory
            with open(setting_path, 'w') as f:
                f.write(directory)

    def show_exception(self, t, val, tb):
        # can get just the offending error from val, but this way will print the entire traceback,
        # maybe we want to give the option to switch between them later?
        msg = ''.join(traceback.format_exception(t, val, tb))
        self.set_console_message(msg, message_type=Console.Error, bold=True)
        self.default_except_hook(t, val, tb)  # this lets the console show the message too

    def remove_image(self, id):
        if id in self.children:
            self.children.pop(id)

        self.last_active = None

    def set_console_message(self, message, message_type=Console.Message, image=None, show_id=True, bold=False,
                            end_new_line=True):
        # Set a message in the console window, colour depends on messageType
        # To get the colours HTML is used
        weight = "normal"
        if bold:
            weight = "bold"

        normal = "<font style=\"font-weight:" + weight + "bold\" color=\"#E6E6E6\">"
        warning = "<font style=\"font-weight:" + weight + "bold\" color=\"#FD971F\">"
        error = "<font style=\"font-weight:" + weight + "bold\" color=\"#F92672\">"
        success = "<font style=\"font-weight:" + weight + "bold\" color=\"#A6E22A\">"
        end = "</font>"
        if end_new_line:
            end += "<br>"

        # construct the message
        output = ""
        if show_id:
            if image is not None:
                message = image.id + ": " + message
            elif image is None and self.last_active is not None:
                message = self.last_active.id + ": " + message

        if message_type == Console.Message:
            output += normal
        if message_type == Console.Warning:
            output += warning
        if message_type == Console.Error:
            output += error
        if message_type == Console.Success:
            output += success

        output += message + end

        curs = self.ui.mainConsole.textCursor()
        curs_start = curs.selectionStart()
        curs_end = curs.selectionEnd()

        # move to end to insert
        curs.movePosition(QtGui.QTextCursor.End)
        self.ui.mainConsole.setTextCursor(curs)
        self.ui.mainConsole.insertHtml(output)

        # move selection back
        curs.setPosition(curs_start)
        curs.setPosition(curs_end, QtGui.QTextCursor.KeepAnchor)
        self.ui.mainConsole.setTextCursor(curs)

        # scroll to bottom
        console_scroll = self.ui.mainConsole.verticalScrollBar()
        console_scroll.setValue(console_scroll.maximum())

    # Qt function
    def closeEvent(self, event):
        # When the main window closes, we want to close all other windows
        keys = list(self.children.keys())  # need to make a copy
        for k in keys:
            self.children[k].close()
        super(MainWindow, self).closeEvent(event)
