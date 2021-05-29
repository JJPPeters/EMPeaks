from PyQt5 import QtCore, QtGui, QtWidgets

from .process_settings_frame_ui import ProcessSettingsFrameUi

import numpy as np
from Processing.Utilities.arrays import IndexedDict


class ProcessSettingsFrame(QtWidgets.QWidget):
    sigApplyFilter = QtCore.pyqtSignal(object)
    signal_result = QtCore.pyqtSignal(object, bool)
    signal_undo = QtCore.pyqtSignal()

    def __init__(self, master, name='Filter', inputs=None, function=None, undo_function=None, show_preview=False,
                 show_apply=False, preserve_image=False, preserve_peaks=False):
        super(ProcessSettingsFrame, self).__init__(master)
        self.master = master
        self.numIn = len(inputs)
        self.controls = IndexedDict()
        self.inputs = inputs

        self.preserve_image = preserve_image
        self.preserve_peaks = preserve_peaks

        self.function = function
        self.undo_function = undo_function

        self.origData = None
        self.orig_peaks = None

        if self.master is not None:
            if self.preserve_image:
                self.origData = np.copy(master.image_plot.image_data)

            if self.preserve_peaks and 'Peaks' in master.plottables:
                self.orig_peaks = np.copy(master.plottables['Peaks'].points)

        # window flags to disable close button, icon etc...
        super(ProcessSettingsFrame, self).__init__(self.master)
        self.ui = ProcessSettingsFrameUi()
        self.ui.setup_ui(self, name, show_preview=show_preview, show_apply=show_apply)

        # add the control elements
        for v in self.inputs:
            if v[0] == "SpinInt":
                self.controls[v[2]] = self.ui.add_spin_int(name=v[2],
                                                           min_val=v[3][0],
                                                           max_val=v[3][1],
                                                           step=v[3][2],
                                                           val=v[3][3])
            elif v[0] == "SpinFloat":
                self.controls[v[2]] = self.ui.add_spin_float(name=v[2],
                                                             min_val=v[3][0],
                                                             max_val=v[3][1],
                                                             step=v[3][2],
                                                             val=v[3][3])
            elif v[0] == "Combo":
                self.controls[v[2]] = self.ui.add_combo_box(name=v[2],
                                                            items=v[3],
                                                            ind=v[4])
            elif v[0] == "ListSelect":
                self.controls[v[2]] = self.ui.add_list_selector(name=v[2],
                                                                items=v[3],
                                                                ind=v[4])
            elif v[0] == "Check":
                self.controls[v[2]] = self.ui.add_check_box(name=v[2],
                                                            checked=v[3])
            elif v[0] == "FileBox":
                self.controls[v[2]] = self.ui.add_get_file_box(name=v[2],
                                                               path=v[3][0],
                                                               extensions=v[3][1])
            elif v[0] == "EditBox":
                self.controls[v[2]] = self.ui.add_edit_box(name=v[2],
                                                           text=v[3])
            elif v[0] == "Slider":
                return

        if self.function is not None:
            self.sigApplyFilter.connect(self.function)

        if self.undo_function is not None:
            self.signal_undo.connect(self.undo_function)

    def get_control_values(self):
        control_values = IndexedDict()

        for key, value in self.controls.items():

            if isinstance(value, QtWidgets.QSpinBox) or isinstance(value, QtWidgets.QDoubleSpinBox):
                control_values[key] = value.value()
            elif isinstance(value, QtWidgets.QComboBox):
                control_values[key] = value.currentText()
            elif isinstance(value, QtWidgets.QCheckBox):
                control_values[key] = value.isChecked()
            elif isinstance(value, QtWidgets.QLineEdit):
                control_values[key] = value.text()
            elif isinstance(value, QtWidgets.QListWidget):
                # remembering that we want checked items, NOT selected ones
                checked_items = []
                for i in range(value.count()):
                    if value.item(i).checkState() == QtCore.Qt.Checked:
                        checked_items.append(value.item(i).text())

                control_values[key] = checked_items

        return control_values

    def apply_action(self):
        control_values = self.get_control_values()
        self.sigApplyFilter.emit(control_values)

    def undo_action(self):
        if self.preserve_image and self.origData is not None:
            self.master.image_plot.set_data(self.origData)

        tag = 'Peaks'

        if self.preserve_peaks:
            if self.orig_peaks is not None:
                self.master.plottables[tag].set_points(self.orig_peaks)
            else:
                self.master.delete_plottable(tag)
            self.master.ui.imageItem.update()

        self.signal_undo.emit()

    # accept args nad kargs as different controls may have different signals, but we don't care
    def on_control_changed(self, *args, **kargs):
        if self.ui.chk_preview is not None and self.ui.chk_preview.checkState() == QtCore.Qt.Checked:
            self.undo_action()
            self.apply_action()

    # Slotfco
    def on_preview_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.apply_action()
        else:
            self.undo_action()

    # Slot
    def on_ok_clicked(self):
        self.undo_action()
        self.apply_action()
        self.signal_result.emit(self, True)
        # self.close()

    # Slot
    def on_cancel_clicked(self):
        self.undo_action()
        self.signal_result.emit(self, False)
        # self.close()
