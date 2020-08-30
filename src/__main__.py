import os
import sys
# import importlib

from PyQt5 import QtGui, QtCore, QtWidgets, QtSvg

import GUI
import GUI.Modules
from GUI.Utilities.enums import Console

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def main():
    #
    # Start by getting the application path
    #

    application_path = None
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(sys.argv[0])

    sys.path.append(application_path)

    #
    #
    #
    app = QtWidgets.QApplication(sys.argv)

    #
    #
    #
    splash_screen = GUI.SplashWindow(application_path)
    splash_screen.show()
    app.processEvents()

    #
    #
    #
    fmt = QtGui.QSurfaceFormat()
    fmt.setRenderableType(QtGui.QSurfaceFormat.OpenGL)
    fmt.setProfile(QtGui.QSurfaceFormat.CoreProfile)
    # fmt.setSamples(4)
    fmt.setVersion(4, 0)
    QtGui.QSurfaceFormat.setDefaultFormat(fmt)

    #
    #
    #
    main_window = GUI.MainWindow(application_path)

    #
    # Load modules
    #
    # first the packaged modules
    module_errors = GUI.Modules.load_modules('Modules', output_func=splash_screen.showMessage)

    # then the user modules
    module_errors += GUI.Modules.load_modules('UserModules', output_func=splash_screen.showMessage)
    if sys.platform.startswith('win'):
        user_module_path = "C:\ProgramData\EMPeaks"
        module_errors += GUI.Modules.load_modules('Modules', modules_path=user_module_path, output_func=splash_screen.showMessage)

    #
    #
    #
    # splash_screen.finish(main_window)
    main_window.show()

    for err in module_errors:
        main_window.set_console_message(err, Console.Warning)

    splash_screen.close()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
