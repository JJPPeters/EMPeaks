from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI import ImageWindow
from GUI.Dialogs import ProcessSettingsDialog

import numpy as np
from scipy import ndimage

from Processing.Image.transformations import affine_transform
from GUI.Controls.Plot.Plottables import Basis
from GUI.Utilities.enums import AnnotationType

class AffineModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Transform']
        self.name = 'Affine'
        self.order_priority = 0

    def run(self):
        if not self.main_window.image_requirements_met():
            return
        # self.main_window.last_active.selectSubBasis('Peaks', 1, 1, self.do_affine_transform)

        la = self.main_window.last_active

        peaks_tag = 'Peaks'
        basis_tag = 'Basis'
        # self.main_window.last_active.selectSubBasis('Peaks', vals[0], vals[1], self.doPeakPairs)

        # def selectSubBasis(self, tag, sublattices, averaging, connect_function, basis_tag='Basis'):
        # self.deleteAnnotation(basis_tag)
        la.delete_plottable(basis_tag, update=True)

        basis = Basis(la.ui.imageItem, num_sub=1, ave_cells=1)

        basis.signal_got_sub_basis.connect(self.do_affine_transform)
        la.add_plottable(basis_tag, basis)

        basis.select_from_points(la.plottables[peaks_tag].points)

    def do_affine_transform(self, basis):
        # TODO: handle 3d images?
        # TODO: output image to new window
        transformed_image = affine_transform(self.active_image_window.image_plot.image_data, basis.vector_coords)
        self.main_window.create_new_image("Affined transformed " + self.main_window.last_active.name, transformed_image)
        # self.main_window.last_active.setImage(transformed_image)
