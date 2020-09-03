import os
from PyQt5 import QtWidgets
# import GUI.main_window as MW
from GUI.Utilities.enums import AnnotationType

from FileIO import ExportPeaks, ExportQuiver


def save_peaks(main_window, tag: str, file_path: str = None):
    if not main_window.image_requirements_met():
        return

    la = main_window.last_active

    if tag in la.plottables and la.plottables[tag].plot_type == AnnotationType.Scatter:
        if file_path is None:
            ext_list = [('Comma separated values', '.csv'), ('Text', '.txt')]
            title = os.path.splitext(la.name)[0] + '_' + tag

            file_path = save_file_helper(main_window, "Save peaks", os.path.join(main_window.last_directory, title), ext_list)

        if file_path is None or file_path == '':
            return

        ExportPeaks(file_path, la.plottables[tag].points)
        main_window.save_settings(os.path.dirname(file_path))


def save_quiver(main_window, tag: str, file_path: str = None):
    if not main_window.image_requirements_met():
        return

    la = main_window.last_active

    if tag in la.plottables and la.plottables[tag].plot_type == AnnotationType.Quiver:
        if file_path is None:
            ext_list = [('Comma separated values', '.csv'), ('Text', '.txt')]
            title = os.path.splitext(la.name)[0] + '_' + tag

            file_path = save_file_helper(main_window, "Save quiver", os.path.join(main_window.last_directory, title), ext_list)

        if file_path is None or file_path == '':
            return

        ExportQuiver(file_path, la.plottables[tag].positions, la.plottables[tag].magnitudes, la.plottables[tag].angles)
        main_window.save_settings(os.path.dirname(file_path))


def save_file_helper(parent, title, start_file, ext_list):
    filter_list = []

    for name, ext in ext_list:
        if ext[0] != '.':
            ext = '.' + ext
        filter_str = name + ' (*' + ext + ')'
        filter_list.append(filter_str)

    filter_str = ''
    for f in filter_list:
        filter_str += f + ';;'

    fpath, filter = QtWidgets.QFileDialog.getSaveFileName(parent, title, start_file, filter_str)

    if fpath == '':
        return None

    if filter not in filter_list:
        raise Exception("Saving file using invalid extension filter")

    i = filter_list.index(filter)

    if ext_list[i][1] != os.path.splitext(fpath)[1]:
        fpath += ext_list[i][1]

    return fpath