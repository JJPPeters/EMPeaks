from GUI.Modules.menu_entry_module import MenuEntryModule
import numpy as np
from GUI.Dialogs.process_settings_dialog import ProcessSettingsDialog
from Processing.PeakPairs import SubPeakPair
from GUI.Controls.Plot.Plottables import Basis
from GUI.Controls.Plot.Plottables import ScatterPlot


class PeakPair(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Process', 'Peaks']
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

        i = 0
        for sub_lattice in pp.subIndices:
            scatter = ScatterPlot(points=affine_peaks[sub_lattice],
                                  size=10,
                                  fill_colour=np.array(next(self.main_window.scatter_cols)) / 255)
            scatter.basis = basis
            self.main_window.last_active.add_plottable('sub' + str(i), scatter)
            # self.main_window.last_active.add_scatter(affinePeaks[sub_lattice], 'sub' + str(i), basis=basis)
            i += 1
