import os
from PyQt5 import QtWidgets


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