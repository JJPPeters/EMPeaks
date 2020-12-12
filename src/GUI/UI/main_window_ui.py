import os

from PyQt5 import QtCore, QtGui, QtWidgets

from GUI.Controls.ImageDisplay.Tabbed import ImageTabWidget
from GUI.Controls.ImageInfoWidget import ImageInfoWidget
from GUI.Menus import FileMenu

import prog_info as Program


# TODO: split these up into sections corresponding to the different menus?
class MainWindowUi(object):

    def __init__(self, main_window, app_path):
        # set title and icon
        main_window.setWindowTitle(Program.Name)
        main_window.setWindowIcon(QtGui.QIcon(os.path.join(app_path, Program.Icon)))

        # make fixed window, might allow resizing later
        # windows is very simple, so resizing not really needed atm
        main_window.setMinimumSize(700, 550)

        # make a generic central widget
        self.centralWidget = QtWidgets.QWidget(main_window)

        # make our layout to hold the two main elements
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # create our info widget
        self.infoPanel = ImageInfoWidget(main_window)

        # create a vertical layout for the main bit (with console underneath)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # create a tab widget to get in the vbox
        self.tabWidget = ImageTabWidget(main_window, parent=self.centralWidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabBar().setMovable(True)
        self.tabWidget.tabBar().setExpanding(True)

        # create the main console to go in the vbox
        self.mainConsole = self.create_console()

        # add them to the vbox
        self.verticalLayout.addWidget(self.tabWidget, 1)
        self.verticalLayout.addWidget(self.mainConsole, 0)

        # add them all to the horizontal layout
        self.horizontalLayout.addWidget(self.infoPanel)
        self.horizontalLayout.addItem(self.verticalLayout)

        main_window.setCentralWidget(self.centralWidget)

        # create the menu bar stuff
        self.menuBar = QtWidgets.QMenuBar(main_window)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 600, 21))

        # create our file menu class
        self.menu_file = FileMenu(main_window, self.menuBar)
        self.menuBar.addAction(self.menu_file.menuAction())

        main_window.setMenuBar(self.menuBar)

        # create a status bar
        self.statusBar = QtWidgets.QStatusBar(main_window)

        self.statusLabel = QtWidgets.QLabel(self.statusBar)
        self.statusLabel.setText("")

        self.statusBar.addWidget(self.statusLabel, 1)

        main_window.setStatusBar(self.statusBar)

    def add_menu(self, menu_list):
        # menu_list = user_module_obj.menu_structure

        current_menu = self.menuBar

        for i in range(len(menu_list)):
            menu_text = [m.text() for m in current_menu.actions()]
            if menu_list[i] in menu_text:
                for m in current_menu.actions():
                    if m.text() == menu_list[i]:
                        if m.menu() is None:
                            raise Exception("Trying to load module under non-menu entry.")

                        current_menu = m.menu()
            else:
                entry = QtWidgets.QMenu(menu_list[i], parent=current_menu)
                current_menu.addAction(entry.menuAction())
                current_menu = entry

        return current_menu

    # at some point, this might want to be it's own class.
    def create_console(self):
        # create a text edit to use as a console (i.e. with status/error messages)
        console = QtWidgets.QTextEdit(self.centralWidget)
        console.setEnabled(True)
        console.setFrameShape(QtWidgets.QFrame.NoFrame)
        console.setFrameShadow(QtWidgets.QFrame.Sunken)
        console.setReadOnly(True)

        # set colour
        palette = console.palette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(22, 22, 19))
        console.setPalette(palette)

        return console
