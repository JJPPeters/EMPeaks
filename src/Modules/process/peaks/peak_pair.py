from GUI.Modules.menu_entry_module import MenuEntryModule
import numpy as np
from GUI.Dialogs.process_settings_dialog import ProcessSettingsDialog
from Processing.PeakPairs import SubPeakPair
from GUI.Controls.Plot.Plottables import Basis
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame
from Processing.Peaks import cluster_peaks_by_intensity

base_path = ['Process', 'Peaks', 'Label']


class PeakPair(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Peak pair'
        self.order_priority = 650

    def run(self):
        if not self.main_window.image_requirements_met():
            return

        if 'Peaks' not in self.main_window.last_active.plottables:
            return

        # TODO: later add in tolerances for calculations
        sublattices = ["SpinInt", 0, "Sub-lattices", (1, 100, 1, 1)]
        averaging = ["SpinInt", 1, "Cell Averaging", (1, 100, 1, 1)]
        threshold = ["SpinFloat", 2, "Threshold", (0, 1, 0.05, 0.3)]

        filterdialog = ProcessSettingsDialog(
            master=self.main_window.last_active,
            name="Peak pair",
            function=self.get_peak_pair_basis,
            inputs=[sublattices, averaging, threshold],
            show_preview=False)
        filterdialog.exec_()

    def get_peak_pair_basis(self, params):
        if not self.main_window.image_requirements_met():
            return
        vals = params

        la = self.main_window.last_active

        peaks_tag = 'Peaks'
        basis_tag = 'Basis'
        # self.main_window.last_active.selectSubBasis('Peaks', vals[0], vals[1], self.doPeakPairs)

        la.delete_plottable(basis_tag, update=True)

        basis = Basis(la.ui.imageItem, num_sub=vals['Sub-lattices'], ave_cells=vals['Cell Averaging'])

        fnc = lambda bss: self.do_peak_pairs(bss, thresh=vals['Threshold'])

        basis.signal_got_sub_basis.connect(fnc)
        la.add_plottable(basis_tag, basis)

        basis.select_from_points(la.plottables[peaks_tag].points)

    def do_peak_pairs(self, basis, thresh=0.3):
        affine_peaks = self.main_window.last_active.plottables['Peaks'].points

        # TODO: I swapped the 1s and 0s here, I don't think it matter but should make sure
        affine_basis = np.array([[0, 1], [1, 0]])
        pp = SubPeakPair(affine_peaks, basis.vector_coords, basis.lattice_coords, affine_basis=affine_basis, thr=thresh)

        for i, sub_lattice in enumerate(pp.subIndices):
            self.create_or_update_scatter('sub' + str(i), affine_peaks[sub_lattice])


class PeaksIntensityCluster(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Intensity cluster'
        self.order_priority = 502

        self.my_clusters = []

    def run(self):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        min_rad = ["SpinInt", 0, "Min radius", (1, 100, 1, 2)]

        # runs as modal dlg
        filter_settings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name="Cluster intensity",
            function=self.do_average_clusters,
            undo_function=self.undo_peaks,
            inputs=[min_rad],
            show_preview=True, show_apply=False, preserve_peaks=True)

        self.add_widget_to_image_window(filter_settings, 0, 2)

    def undo_peaks(self):
        for name in self.my_clusters:
            self.create_or_update_scatter(name, None)

    def do_average_clusters(self, params):
        tag = 'Peaks'
        if not self.main_window.image_requirements_met():
            return

        peaks = self.main_window.last_active.plottables[tag].points
        image = self.main_window.last_active.image_plot.intensities

        new_peaks = cluster_peaks_by_intensity(image, peaks, clusters=params[0])

        i = 0
        new_clusters = []
        for p in new_peaks:
            name = 'cluster' + str(i)
            self.create_or_update_scatter(name, p)
            self.my_clusters.append(name)
            new_clusters.append(name)
            i += 1

        for j in range(i, len(self.my_clusters)):
            name = 'cluster' + str(i)
            self.create_or_update_scatter(name, None)

        self.my_clusters = new_clusters
