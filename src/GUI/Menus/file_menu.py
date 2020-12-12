import os

from PyQt5 import QtGui, QtWidgets
import numpy as np

#
# Currently for expoerting the workspace
import h5py
from Processing.Utilities import LatticeBasis
from GUI.Controls.Plot.Plottables import Basis
#

from GUI.Utilities import save_peaks
from FileIO import ImportPeaks, ExportPeaks, ImportImage, ExportImage, ExportRGB
from GUI.Dialogs import ProcessSettingsDialog
import GUI

# from GUI.image_window import ImageWindow
from GUI.Utilities.enums import Console, AnnotationType
from GUI.Controls import MenuEntry
from GUI.Utilities import save_file_helper

from GUI.Controls.Plot.Plottables import ImagePlot, ScatterPlot, QuiverPlot, LinePlot, HistogramPlot, PolarImagePlot

from Processing.Image import rgb_array_to_greyscale

import imageio

from GUI.Controls import ImageDisplayWidget


class FileMenu(MenuEntry):
    def __init__(self, master, parent_menu):
        super(FileMenu, self).__init__("File", parent=parent_menu)

        self.master = master

        self.createAction("Open...", self.on_action_open_file_triggered, shortcut="Ctrl+O")

        self.menu_save = self.createMenu("Save...")
        self.menu_save.createAction("Workspace...", self.on_action_save_workspace)
        self.menu_save.createAction("Data...", self.on_action_save_image_as_data)
        self.menu_save.createAction("Display...", self.on_action_save_display)

        self.menu_peaks = self.createMenu("Peaks...")
        self.menu_peaks.createAction("Import...", self.on_action_import_peaks_triggered)
        self.menu_peaks.createAction("Export...", lambda: self.on_action_export_peaks_triggered('Peaks'))

    def on_action_open_file_triggered(self):
        fpath = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open file", self.master.last_directory,
            "All supported (*.h5 *.dm3 *.dm4 *.tif *.npy);;HDF5 (*.h5);;Digital micrograph (*.dm3 *.dm4);;Tiff ("
            "*.tif);;Numpy (*.npy)")
        fpath = fpath[0]

        if fpath == "":
            return

        try:
            image_dict = ImportImage(fpath)
        except Exception:
            self.master.set_console_message("File not valid", Console.Warning)
            return  # some sort of warning here?

        self.master.save_settings(os.path.dirname(fpath))

        self.process_open_dict(image_dict, os.path.basename(fpath))

    def on_action_save_image_as_data(self):
        if not self.master.image_requirements_met():
            return

        ext_list = [('Tiff', '.tif'), ('Numpy', '.npy')]
        title = os.path.splitext(self.master.last_active.name)[0]

        fpath = save_file_helper(self, "Save data", os.path.join(self.master.last_directory, title), ext_list)

        if fpath is None:
            return

        im_data = self.master.last_active.image_plot.image_data
        ExportImage(fpath, im_data)
        self.master.save_settings(os.path.dirname(fpath))

    def on_action_save_display(self):
        if not self.master.image_requirements_met():
            return

        ext_list = [('Png', '.png'), ('Bmp', '.bmp')]
        title = os.path.splitext(self.master.last_active.name)[0]

        fpath = save_file_helper(self, "Save display", os.path.join(self.master.last_directory, title), ext_list)

        if fpath is None:
            return

        # use dialog to get parameters
        scaling = ["SpinInt", 0, "Image scaling", (1, 100, 1, 1)]
        fit_view = ["Check", 1, "Export current view", False]
        annotations = ["Check", 2, "Include annotations", True]
        grey = ["Check", 3, "Export greyscale", False]

        filterdialog = ProcessSettingsDialog(master=self.master.last_active,
                                             name="Save display",  # TODO: add old name to this?
                                             inputs=[scaling, fit_view, annotations, grey])

        func = lambda i: self.do_save_display(i, fpath)

        filterdialog.sigApplyFilter.connect(func)
        filterdialog.exec_()

        filterdialog.sigApplyFilter.disconnect(func)

    def do_save_display(self, params, path):
        im_scale = params['Image scaling']
        current_view = params['Export current view']
        keep_annotations = params['Include annotations']
        greyscale = params['Export greyscale']

        im = self.master.last_active.ui.imageItem.export_display(scale=im_scale,
                                                                 fit_view=not current_view,
                                                                 image_only=not keep_annotations)

        if greyscale:
            im = rgb_array_to_greyscale(im)

        imageio.imsave(path, im)

    def on_action_import_peaks_triggered(self):
        tag = 'Peaks'
        if not self.master.image_requirements_met():
            return

        fpath = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open file", self.master.last_directory,
                "Comma separated values (*.csv);;Text (*.txt)")
        fpath = fpath[0]
        ftype = os.path.splitext(fpath)[1]

        if ftype != ".csv" and ftype != ".txt":
            return

        if tag in self.master.last_active.plottables:
            quit_msg = "This will override existing peaks"
            reply = QtWidgets.QMessageBox.question(self.master, 'Warning', quit_msg,
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Cancel:
                return

        peaks = ImportPeaks(fpath)

        #  Why did I do this?
        # if peaks.ndim < 2:
        #     peaks = peaks.reshape((1, peaks.size))

        self.master.save_settings(os.path.dirname(fpath))

        scatter = ScatterPlot(peaks, size=10, fill_colour=np.array(next(self.master.scatter_cols)) / 255)

        self.master.last_active.add_plottable(tag, scatter)

    def on_action_export_peaks_triggered(self, tag, fpath=None):
        save_peaks(self.master, tag, fpath)

    def on_action_save_workspace(self):
        if not self.master.image_requirements_met():
            return

        ext_list = [('hdf5', '.h5')]
        title = os.path.splitext(self.master.last_active.name)[0]

        fpath = save_file_helper(self, "Save data", os.path.join(self.master.last_directory, title), ext_list)

        if fpath is None:
            return

        self.master.save_settings(os.path.dirname(fpath))

        with h5py.File(fpath, 'w') as hf:

            hf.attrs['program'] = 'pypeaks'
            # hf.attrs['program_version'] = 0.1

            # TODO: only make groups when they are needed
            if any(v.plot_type == AnnotationType.Scatter for v in self.master.last_active.plottables.values()):
                peak_grp = hf.create_group('peaks')
            if any(v.plot_type == AnnotationType.Basis for v in self.master.last_active.plottables.values()):
                basis_grp = hf.create_group('bases')
            if any(v.plot_type == AnnotationType.Image for v in self.master.last_active.plottables.values()):
                image_grp = hf.create_group('images')
            if any(v.plot_type == AnnotationType.Polar for v in self.master.last_active.plottables.values()):
                image_grp = hf.create_group('polar_images')
            if any(v.plot_type == AnnotationType.Quiver for v in self.master.last_active.plottables.values()):
                quiver_grp = hf.create_group('quivers')

            for key, val in self.master.last_active.plottables.items():
                #
                # image data
                #
                # TODO: account for potential multiple images?
                if val.plot_type == AnnotationType.Image:

                    image_data = self.master.last_active.image_plot.image_data

                    key_grp = image_grp.create_group(key)

                    key_grp.attrs['visible'] = val.visible

                    key_grp.create_dataset('magnitude', data=image_data)
                    # TODO: here we can have things like image calibration and so on

                if val.plot_type == AnnotationType.Polar:

                    image_mag = self.master.last_active.image_plot.magnitude_data
                    image_ang = self.master.last_active.image_plot.angle_data

                    key_grp = image_grp.create_group(key)

                    key_grp.attrs['visible'] = val.visible

                    key_grp.create_dataset('magnitude', data=image_mag)
                    key_grp.create_dataset('angle', data=image_ang)

                #
                # Peak positions
                #
                if val.plot_type == AnnotationType.Scatter:
                    key_grp = peak_grp.create_group(key)
                    p_data = val.points
                    key_grp.create_dataset('data', data=p_data)

                    key_grp.attrs['visible'] = val.visible

                #
                # Handle saving the basis objects themselves (not always the same as the peak ones)
                #
                if val.plot_type == AnnotationType.Basis:
                    basis = val.basis
                    key_grp = basis_grp.create_group(key)

                    key_grp.attrs['visible'] = val.visible

                    a_vec, b_vec = basis.get_basis_vectors()

                    key_grp.attrs['a'] = a_vec
                    key_grp.attrs['b'] = b_vec
                    key_grp.attrs['coords'] = basis.lattice_coords

                #
                # Handle saving the quiver objects
                #
                if val.plot_type == AnnotationType.Quiver:
                    key_grp = quiver_grp.create_group(key)

                    key_grp.attrs['visible'] = val.visible

                    key_grp.create_dataset('position', data=val.positions)
                    key_grp.create_dataset('magnitude', data=val.magnitudes)
                    key_grp.create_dataset('angle', data=val.angles)
                    key_grp.create_dataset('scale', data=val.scale)

    def process_open_dict(self, in_dict, title):

        image_id = self.master.generate_window_id()

        image_display = ImageDisplayWidget(title, image_id)
        self.master.children[image_id] = image_display
        self.master.ui.tabWidget.addTab(image_display, f"{image_id}:{title}")

        ti = self.master.ui.tabWidget.indexOf(image_display)
        self.master.ui.tabWidget.setCurrentIndex(ti)

        # image_window = GUI.ImageWindow(title, image_id, master=self.master)
        # image_window.show()

        # image_display = image_window.ui.plot

        for key, val in in_dict.items():
            if key == 'images':
                for k, v in val.items():
                    visible = True
                    if 'visible' in v.keys():
                        visible = v['visible']

                    # create our image plottable
                    image_plot = ImagePlot(v['magnitude'], visible=visible)
                    image_display.set_image_plot(image_plot)

            if key == 'polar_images':
                for k, v in val.items():
                    visible = True
                    if 'visible' in v.keys():
                        visible = v['visible']

                    # create our image plottable
                    image_plot = PolarImagePlot(angle=v['angle'], magnitude=v['magnitude'], visible=visible)
                    image_display.set_image_plot(image_plot)

            if key == 'peaks':
                for k, v in val.items():
                    peak_data = v['data']

                    visible = True
                    if 'visible' in v.keys():
                        visible = v['visible']

                    scatter = ScatterPlot(points=peak_data,
                                          size=10,
                                          visible=visible,
                                          fill_colour=np.array(next(self.master.scatter_cols)) / 255)
                    image_display.add_plottable(k, scatter)

            if key == 'bases':
                for k, v in val.items():
                    basis_coords = v['coords']
                    basis_a = v['a']
                    basis_b = v['b']

                    basis = LatticeBasis(basis_coords.shape[0])
                    basis.set_from_coords_and_vectors(basis_coords, basis_a, basis_b)

                    visible = True
                    if 'visible' in v.keys():
                        visible = v['visible']

                    # now need to create the drawn basis object?
                    basis_annotation = Basis(image_display.plot, basis=basis)
                    basis_annotation.visible = visible

                    image_display.add_plottable(k, basis_annotation)

            if key == 'quivers':
                for k, v in val.items():
                    mag = v['magnitude']
                    ang = v['angle']
                    pos = v['position']
                    sc = v['scale']

                    visible = True
                    if 'visible' in val.keys():
                        visible = val['visible']

                    quiver_annotation = QuiverPlot(pos, mag, ang, visible=visible, scale=sc)

                    image_display.add_plottable(k, quiver_annotation)

        # TODO: re-implement this
        self.master.set_console_message("Opened file \"" + title, Console.Success, image=image_display)
