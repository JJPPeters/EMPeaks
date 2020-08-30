from PyQt5 import QtCore, QtGui, QtWidgets


class ProcessSettingsFrameUi(object):
    def __init__(self):
        self.filter_widget = None

        self.title_label = None

        self.btn_cancel = None
        self.btn_ok = None
        self.chk_preview = None

        self.vert_layout = None
        self.vert_control_layout = None
        self.horz_preview_layout = None
        self.horz_cancel_ok_layout = None

    def setup_ui(self, filter_widget, name, show_preview=False, show_apply=False):
        self.filter_widget = filter_widget
        # this is the main layout
        self.vert_layout = QtWidgets.QVBoxLayout(self.filter_widget)

        # this sets the title, can be hidden for dialog use
        self.title_label = QtWidgets.QLabel(self.filter_widget)
        self.title_label.setTextFormat(QtCore.Qt.RichText)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.vert_layout.addWidget(self.title_label)

        # this is where the dynamic controls are kept
        self.vert_control_layout = QtWidgets.QVBoxLayout()

        self.vert_layout.addLayout(self.vert_control_layout)

        # not we can set up a layout for the preview/ok/cancel buttons
        # (this bit is quite lengthy)
        if show_preview or show_apply:
            self.horz_preview_layout = QtWidgets.QHBoxLayout()
            spacer_item_1 = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            self.horz_preview_layout.addItem(spacer_item_1)
            self.vert_layout.addLayout(self.horz_preview_layout)
        if show_preview:
            self.chk_preview = QtWidgets.QCheckBox(self.filter_widget)
            self.chk_preview.setChecked(False)
            self.horz_preview_layout.addWidget(self.chk_preview)
        elif show_apply:
            self.btn_apply = QtWidgets.QPushButton(self.filter_widget)
            self.horz_preview_layout.addWidget(self.btn_apply)


        self.horz_cancel_ok_layout = QtWidgets.QHBoxLayout()
        spacer_item_2 = QtWidgets.QSpacerItem(
            1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horz_cancel_ok_layout.addItem(spacer_item_2)
        self.btn_cancel = QtWidgets.QPushButton(self.filter_widget)
        self.horz_cancel_ok_layout.addWidget(self.btn_cancel)
        self.btn_ok = QtWidgets.QPushButton(self.filter_widget)
        self.horz_cancel_ok_layout.addWidget(self.btn_ok)
        self.vert_layout.addLayout(self.horz_cancel_ok_layout)

        spacer_item_3 = QtWidgets.QSpacerItem(
            1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vert_layout.addItem(spacer_item_3)

        self.vert_layout.setStretch(2, 1)

        # set the names of everything
        self.retranslate_ui(name, show_preview, show_apply)
        
        # connect our slots
        self.connect_slots(show_preview, show_apply)

        # set the size
        new_size = self.filter_widget.sizeHint()
        self.filter_widget.resize(new_size)
        self.filter_widget.setFixedWidth(new_size.width())

    def connect_slots(self, show_preview, show_apply):
        self.btn_ok.clicked.connect(self.filter_widget.on_ok_clicked)
        self.btn_cancel.clicked.connect(self.filter_widget.on_cancel_clicked)
        if show_preview:
            self.chk_preview.stateChanged.connect(self.filter_widget.on_preview_changed)
        elif show_apply:
            self.btn_apply.clicked.connect(self.filter_widget.apply_action)

    def retranslate_ui(self, name, show_preview, show_apply):
        self.title_label.setText('<b>' + name + '<\\b>')
        self.btn_cancel.setText("Cancel")
        self.btn_ok.setText("OK")
        if show_preview:
            self.chk_preview.setText("Preview")
        elif show_apply:
            self.btn_apply.setText("Apply")

    def add_spin_int(self, name="Int Spin", min_val=0, max_val=100, step=1, val=1):
        name += ":"
        vert_control_layout = QtWidgets.QVBoxLayout()
        lbl_spin_int = QtWidgets.QLabel(self.filter_widget)
        vert_control_layout.addWidget(lbl_spin_int)

        spin_int = QtWidgets.QSpinBox(self.filter_widget)
        spin_int.setMaximum(max_val)
        spin_int.setMinimum(min_val)
        spin_int.setSingleStep(step)
        spin_int.setValue(val)

        vert_control_layout.addWidget(spin_int)
        self.vert_control_layout.addLayout(vert_control_layout)

        lbl_spin_int.setText(name)

        spin_int.valueChanged.connect(self.filter_widget.on_control_changed)

        return spin_int

    def add_spin_float(self, name="Float Spin", min_val=0, max_val=100, step=0.25, val=1):
        name += ":"
        vert_control_layout = QtWidgets.QVBoxLayout()
        lbl_spin_float = QtWidgets.QLabel(self.filter_widget)
        vert_control_layout.addWidget(lbl_spin_float)

        spin_float = QtWidgets.QDoubleSpinBox(self.filter_widget)
        spin_float.setMaximum(max_val)
        spin_float.setMinimum(min_val)
        spin_float.setSingleStep(step)
        spin_float.setValue(val)

        vert_control_layout.addWidget(spin_float)
        self.vert_control_layout.addLayout(vert_control_layout)

        lbl_spin_float.setText(name)

        spin_float.valueChanged.connect(self.filter_widget.on_control_changed)

        return spin_float

    def add_combo_box(self, name="Combo Box", items=None, ind=-1):
        name += ":"
        vert_control_layout = QtWidgets.QVBoxLayout()
        lbl_combo_box = QtWidgets.QLabel(self.filter_widget)
        vert_control_layout.addWidget(lbl_combo_box)

        combo_box = QtWidgets.QComboBox(self.filter_widget)
        combo_box.addItems(items)
        combo_box.setCurrentIndex(ind)

        vert_control_layout.addWidget(combo_box)
        self.vert_control_layout.addLayout(vert_control_layout)

        lbl_combo_box.setText(name)

        combo_box.currentIndexChanged.connect(self.filter_widget.on_control_changed)

        return combo_box

    def add_list_selector(self, name="List Selector", items=None, ind=None):
        name += ":"
        vert_control_layout = QtWidgets.QVBoxLayout()
        lbl_list_selector = QtWidgets.QLabel(self.filter_widget)
        vert_control_layout.addWidget(lbl_list_selector)

        list_selector = QtWidgets.QListWidget(self.filter_widget)
        # list_selector.addItems(items)
        # list_selector.setCurrentIndex(ind)
        for item in items:
            i = QtWidgets.QListWidgetItem(item)
            i.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            i.setCheckState(QtCore.Qt.Unchecked)  # this is important to getting the cehckboxes to show
            list_selector.addItem(i)

        if ind is not None:
            for i in range(list_selector.count()):
                if i in ind:
                    list_selector.item(i).setCheckState(QtCore.Qt.Checked)

        vert_control_layout.addWidget(list_selector)
        self.vert_control_layout.addLayout(vert_control_layout)

        lbl_list_selector.setText(name)

        list_selector.itemChanged.connect(self.filter_widget.on_control_changed)

        return list_selector

    def add_check_box(self, name="Check Box", checked=False):
        check_box = QtWidgets.QCheckBox(self.filter_widget)
        check_box.setChecked(checked)
        check_box.setText(name)

        self.vert_control_layout.addWidget(check_box)

        check_box.stateChanged.connect(self.filter_widget.on_control_changed)

        return check_box