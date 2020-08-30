from GUI.Modules.menu_entry_module import MenuEntryModule
from Processing.DisplacementAnalysis import abo_displacement_field, abo_displacement
from GUI.Dialogs import ProcessSettingsDialog
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame
from GUI import ImageWindow
from GUI.Utilities import std_colour_maps
from GUI.Utilities.enums import AnnotationType
from GUI.Controls.Plot.Plottables import QuiverPlot, PolarImagePlot, ImagePlot

import numpy as np
import os
from PyQt5 import QtGui, QtCore

base_path = ['Process', 'Map', 'Displacements']


class DisplacementVectors(MenuEntryModule):
    def __init__(self):
        self.menu_structure = base_path
        self.name = 'Vectors'
        self.order_priority = 0

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        default = 0

        items = []
        for key, entry in self.main_window.last_active.plottables.items():
            if entry.plot_type == AnnotationType.Scatter:
                items.append(key)

        if len(items) < 2:
            return

        try:
            ref_index = items.index('sub0')
        except ValueError:
            ref_index = default
            default += 1

        try:
            disp_index = items.index('sub1')
        except ValueError:
            disp_index = default

        ref_combo = ["ListSelect", 0, "Reference", items, [ref_index]]
        disp_combo = ["ListSelect", 1, "Displacement", items, [disp_index]]
        neighbours_spin = ["SpinInt", 2, "Neighbours", (2, 20, 1, 4)]
        scale_spin = ["SpinFloat", 3, "Scale", (0.1, 100, 1, 10)]
        average_spin = ["SpinInt", 4, "Average neighbours", (0, 100, 1, 0)]
        limit_spin = ["SpinFloat", 5, "Limit", (0.0, 100, 0.1, 0.2)]

        filter_settings = ProcessSettingsFrame(master=self.main_window.last_active,
                                               name="Map",
                                               function=self.do_displacement_vectors,
                                               inputs=[ref_combo,
                                               disp_combo,
                                               neighbours_spin,
                                               scale_spin,
                                               average_spin,
                                               limit_spin],
                                               show_preview=False)

        self.add_widget_to_image_window(filter_settings, 0, 2)

    def do_displacement_vectors(self, params):
        # image = params[0]
        vals = params

        ref_col = vals['Reference']
        disp_col = vals['Displacement']
        neighbours = vals['Neighbours']
        scale = vals['Scale']
        average = vals["Average neighbours"]
        limit_factor = vals['Limit']

        ref_list = [self.main_window.last_active.plottables[x].points for x in ref_col]
        disp_list = [self.main_window.last_active.plottables[x].points for x in disp_col]

        ref_peaks = np.concatenate(ref_list, axis=0)
        disp_peaks = np.concatenate(disp_list, axis=0)

        if ref_peaks is None or disp_peaks is None:
            return

        limit = None
        for ref in ref_col:
            basis = self.main_window.last_active.plottables[ref].basis

            if basis is not None:
                temp = basis.get_largest_vector() * limit_factor
                if limit is None or temp > limit:
                    limit = temp

        position, polar_displacement = abo_displacement(ref_peaks, disp_peaks, neighbours,
                                                        limit=limit, polar=True, average=average)

        # self.main_window.last_active.plot_arrows(position, displacement, "displacements", scale=scale)
        # self.main_window.last_active.add_quiver(position, polar_displacement[0], polar_displacement[1],
        #                                    "displacements", scale=scale)
        q = QuiverPlot(position, polar_displacement[0], polar_displacement[1], scale=scale)

        self.main_window.last_active.add_plottable("Displacements", q)


class DisplacementField(MenuEntryModule):
    def __init__(self):
        self.menu_structure = base_path
        self.name = 'Field'
        self.order_priority = 0

        self.new_window = None

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        default = 0

        items = []
        for key, entry in self.main_window.last_active.plottables.items():
            if entry.plot_type == AnnotationType.Scatter:
                items.append(key)

        if len(items) < 2:
            return

        try:
            ref_index = items.index('sub0')
        except ValueError:
            ref_index = default
            default += 1

        try:
            disp_index = items.index('sub1')
        except ValueError:
            disp_index = default

        ref_combo = ["ListSelect", 0, "Reference", items, [ref_index]]
        disp_combo = ["ListSelect", 1, "Displacement", items, [disp_index]]
        neighbours_spin = ["SpinInt", 2, "Neighbours", (2, 20, 1, 4)]
        direction_combo = ["Combo", 3, "Direction", ('360°', 'Vertical', 'Horizontal'), 0]
        interp_combo = ["Combo", 4, "Interpolation", ('Nearest', 'Linear', 'Cubic'), 0]
        limit_spin = ["SpinFloat", 5, "Scale", (0.0, 100, 0.1, 0.2)]
        average_spin = ["SpinInt", 6, "Average neighbours", (0, 100, 1, 0)]
        norm_check = ["Check", 7, "Normalise", False]

        filterdialog = ProcessSettingsDialog(master=self.active_image_window,
                                             function=self.do_displacement_map,
                                             name="Map",
                                             inputs=[ref_combo,
                                            disp_combo,
                                            neighbours_spin,
                                            direction_combo,
                                            interp_combo,
                                            limit_spin,
                                            average_spin,
                                            norm_check],
                                             show_preview=False)
        filterdialog.exec()

        if self.new_window is not None:
            # TODO: I don't like having to do this, but this is the only way to force the new window to get focus
            self.new_window.activateWindow()
        self.new_window = None

    def do_displacement_map(self, params):
        # image = params[0]
        vals = params

        ref_col = vals["Reference"]
        disp_col = vals["Displacement"]
        neighbours = vals["Neighbours"]
        direction = vals["Direction"]
        interp_method = vals["Interpolation"].lower()
        limit_factor = vals["Scale"]
        average = vals["Average neighbours"]
        norm = vals["Normalise"]

        ref_list = [self.main_window.last_active.plottables[x].points for x in ref_col]
        disp_list = [self.main_window.last_active.plottables[x].points for x in disp_col]

        ref_peaks = np.concatenate(ref_list, axis=0)
        disp_peaks = np.concatenate(disp_list, axis=0)

        shp = self.main_window.last_active.image_plot.image_data.shape
        title = self.main_window.last_active.name

        limit = None
        for ref in ref_col:
            basis = self.main_window.last_active.plottables[ref].basis

            if basis is not None:
                temp = basis.get_largest_vector() * limit_factor
                if limit is None or temp > limit:
                    limit = temp

        if ref_peaks is not None and disp_peaks is not None:
            magnitude, angle = abo_displacement_field(ref_peaks, disp_peaks, shp[0], shp[1], neighbours, direction,
                                                      method=interp_method, limit=limit, average=average)

            if norm:
                magnitude[:] = 1

            im_id = self.main_window.generate_window_id()

            if direction == '360°':
                self.new_window = ImageWindow(title + ' displacement field ' + direction,
                                               im_id, master=self.main_window)
                self.new_window.show()

                # new_image_window.activateWindow()
                self.new_window.raise_()
                # new_image_window.setFocus()

                image = PolarImagePlot(angle, magnitude)
                self.new_window.set_image_plot(image)

                self.main_window.Children[im_id] = self.new_window

                self.main_window.last_active = self.new_window
                self.main_window.ui.infoPanel.changeColMap(std_colour_maps['RPBY360'])

            else:
                self.new_window = ImageWindow(title + ' displacement field ' + direction.lower(),
                                              im_id, master=self.main_window)
                self.new_window.show()

                image = ImagePlot(magnitude)
                self.new_window.set_image_plot(image)

                self.main_window.Children[im_id] = self.new_window


class DisplacementExport(MenuEntryModule):
    def __init__(self):
        self.menu_structure = base_path
        self.name = 'Export'
        self.order_priority = 0

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        # if not self.main_window.last_active.haveScatter(2):
        #     return

        default = 0

        items = []
        for key, entry in self.main_window.last_active.plottables.items():
            if entry.plot_type == AnnotationType.Scatter:
                items.append(key)

        try:
            ref_index = items.index('sub0')
        except ValueError:
            ref_index = default
            default += 1

        try:
            disp_index = items.index('sub1')
        except ValueError:
            disp_index = default

        ref_combo = ["ListSelect", 0, "Reference", items, [ref_index]]
        disp_combo = ["ListSelect", 1, "Displacement", items, [disp_index]]
        average_spin = ["SpinInt", 2, "Average neighbours", (0, 100, 1, 0)]
        neighbours_spin = ["SpinInt", 3, "Neighbours", (2, 20, 1, 4)]

        filterdialog = ProcessSettingsDialog(master=self.main_window.last_active,
                                             name="Map",
                                             function=self.do_displacement_vectors,
                                             inputs=[ref_combo,
                                            disp_combo,
                                            average_spin,
                                            neighbours_spin],
                                             show_preview=False)
        filterdialog.exec_()

    def do_displacement_export(self, params):
        # image = params[0]
        vals = params

        ref_col = vals["Reference"]
        disp_col = vals["Displacement"]
        average = vals["Average neighbours"]
        neighbours = vals["Neighbours"]

        ref_list = [self.main_window.last_active.plottables[x].points for x in ref_col]
        disp_list = [self.main_window.last_active.plottables[x].points for x in disp_col]

        ref_peaks = np.concatenate(ref_list, axis=0)
        disp_peaks = np.concatenate(disp_list, axis=0)

        if ref_peaks is None or disp_peaks is None:
            return

        position, displacement = abo_displacement(ref_peaks, disp_peaks, neighbours, average=average)

        title = os.path.splitext(self.main_window.last_active.name)[0]
        fpath = QtGui.QFileDialog.getSaveFileName(
            self, "Save file", os.path.join(self.main_window.last_directory, title) + "_displacements",
            "Comma separated values (*.csv);;Text (*.txt)")
        fpath = fpath[0]

        if fpath == "":
            return

        np.savetxt(fpath, np.hstack((np.fliplr(position), np.fliplr(displacement))),
                   delimiter=",", header="x,y,dx,dy")
