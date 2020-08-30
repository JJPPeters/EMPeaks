from PyQt5 import QtCore, QtGui, QtWidgets

from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame


class ProcessSettingsDialog(QtWidgets.QDialog):
    def __init__(self, master, name="Dialog", inputs=None, function=None, show_preview=False, show_apply=False,
                 preserve_image=False, preserve_peaks=False):
        super(ProcessSettingsDialog, self).__init__(master)

        # setup the ui parts:
        # self.setModal(True)
        self.setWindowTitle(name)

        self.dialog_layout = QtWidgets.QVBoxLayout(self)
        self.dialog_layout.setSpacing(0)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)

        self.dialog_widget = ProcessSettingsFrame(master,
                                                  inputs=inputs,
                                                  function=function,
                                                  show_preview=show_preview,
                                                  show_apply=show_apply,
                                                  preserve_image=preserve_image,
                                                  preserve_peaks=preserve_peaks)
        self.dialog_widget.ui.title_label.hide()
        self.dialog_widget.signal_result.connect(self.set_result)

        self.dialog_layout.addWidget(self.dialog_widget)

        self.setLayout(self.dialog_layout)

        new_size = self.minimumSizeHint()
        self.setFixedSize(new_size)

    def __getattr__(self, attr):
        return getattr(self.dialog_widget, attr)

    def get_control_values(self):
        return self.dialog_widget.get_control_values()

    def set_result(self, widget, state):
        self.setResult(state)
        self.close()

    def closeEvent(self, e):
        # TODO: I've done something funny, where I need this for the returned result to be correct!
        # super(FilterDialog, self).closeEvent(e)
        return