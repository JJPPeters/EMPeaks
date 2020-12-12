from GUI.Modules.menu_entry_module import MenuEntryModule
from GUI.Dialogs.process_settings_dialog import ProcessSettingsDialog
from Processing.Registration import rigid_align, overdetermined_rigid_align, pyramid_rigid_align
import numpy as np

base_path = ['Process', 'Stack', 'Registration']


class RigidAlign(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Rigid align'
        self.order_priority = 200

    def run(self):
        if not self.main_window.image_requirements_met() or self.active_image_window.image_plot.image_data.ndim != 3:
            return

        n = self.active_image_window.image_plot.image_data.shape[2]
        sublattices = ["SpinInt", 0, "Reference slice", (0, n, 1, 0)]
        average_reference = ["Check", 1, "Average reference", False]
        crop = ["Check", 2, "Crop output", True]
        output_stack = ["Check", 3, "Output stack", True]
        output_average = ["Check", 4, "Output average", True]

        filterdialog = ProcessSettingsDialog(
            master=self.main_window.last_active,
            name="Rigid registration",
            function=self.do_rigid_align,
            inputs=[sublattices, average_reference, crop, output_stack, output_average],
            show_preview=False)
        filterdialog.exec_()

    def do_rigid_align(self, params):
        ref = params['Reference slice']
        ref_ave = params['Average reference']
        crop = params['Crop output']
        out_stack = params['Output stack']
        out_ave = params['Output average']

        outputs = rigid_align(self.active_image_window.image_plot.image_data, ref, ref_ave, crop, out_stack, out_ave)

        # outputs will always have a 'cumulative_shifts' entry

        if 'averaged_stack' in outputs:  # we have an aligned stack
            self.main_window.create_new_image("Averaged " + self.main_window.last_active.name, outputs['averaged_stack'])
        if 'aligned_stack' in outputs:  # we have the averaged image
            self.main_window.create_new_image("Aligned " + self.main_window.last_active.name, outputs['aligned_stack'])
        # if 'cumulative_shifts' in outputs:  # we have the displacement data
        #     imageid = self.main_window.generate_image_id()
        #     newimagewindow = ControlGraphWindow("Shifts of " + self.main_window.last_active.name, imageid,
        #                                         master=self.main_window)
        #     newimagewindow.show()
        #     shifts = outputs['cumulative_shifts']
        #     newimagewindow.addPlot('x', np.arange(shifts.shape[0]), shifts[:, 0])
        #     newimagewindow.addPlot('y', np.arange(shifts.shape[0]), shifts[:, 1])
        #     newimagewindow.setXLabel('Slice')
        #     newimagewindow.setYLabel('Shift (pixels)')
        #     self.main_window.children[imageid] = newimagewindow


class OverdeterminedRigidAlign(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Overdetermined rigid align'
        self.order_priority = 201

    def run(self):
        if not self.main_window.image_requirements_met() or self.active_image_window.image_plot.image_data.ndim != 3:
            return

        crop = ["Check", 0, "Crop output", True]
        output_stack = ["Check", 1, "Output stack", True]
        output_average = ["Check", 2, "Output average", True]

        filterdialog = ProcessSettingsDialog(
            master=self.main_window.last_active,
            name="Rigid registration",
            function=self.do_overdetermined_rigid_align,
            inputs=[crop, output_stack, output_average],
            show_preview=False)
        filterdialog.exec_()

    def do_overdetermined_rigid_align(self, params):
        crop = params['Crop output']
        out_stack = params['Output stack']
        out_average = params['Output average']

        outputs = overdetermined_rigid_align(self.active_image_window.image_plot.image_data, crop, out_stack, out_average)

        # outputs will always have a 'cumulative_shifts' entry
        if 'averaged_stack' in outputs:  # we have an aligned stack
            self.main_window.create_new_image("Averaged " + self.main_window.last_active.name,
                                              outputs['averaged_stack'])
        if 'aligned_stack' in outputs:  # we have the averaged image
            self.main_window.create_new_image("Aligned " + self.main_window.last_active.name, outputs['aligned_stack'])


class PyramidRigidAlign(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = base_path
        self.name = 'Pyramid rigid align'
        self.order_priority = 202

    def run(self):
        if not self.main_window.image_requirements_met() or self.active_image_window.image_plot.image_data.ndim != 3:
            return

        n = self.active_image_window.image_plot.image_data.shape[2]
        pyramid_size = ["SpinInt", 0, "Pyramid size", (1, n, 1, 3)]
        crop = ["Check", 1, "Crop output", True]
        output_stack = ["Check", 2, "Output stack", True]
        output_average = ["Check", 3, "Output average", True]

        filterdialog = ProcessSettingsDialog(
            master=self.main_window.last_active,
            name="Rigid registration",
            function=self.do_pyramid_rigid_align,
            inputs=[pyramid_size, crop, output_stack, output_average],
            show_preview=False)
        filterdialog.exec_()

    def do_pyramid_rigid_align(self, params):
        pyramid_size = params['Pyramid size']
        crop = params['Crop output']
        out_stack = params['Output stack']
        out_average = params['Output average']
        outputs = pyramid_rigid_align(self.active_image_window.image_plot.image_data, pyramid_size, crop, out_stack, out_average)

        # outputs will always have a 'cumulative_shifts' entry
        if 'averaged_stack' in outputs:  # we have an aligned stack
            self.main_window.create_new_image("Averaged " + self.main_window.last_active.name,
                                              outputs['averaged_stack'])
        if 'aligned_stack' in outputs:  # we have the averaged image
            self.main_window.create_new_image("Aligned " + self.main_window.last_active.name, outputs['aligned_stack'])
