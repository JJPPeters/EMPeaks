from GUI.Modules.menu_entry_module import MenuEntryModule
import numpy as np
import math

from PyQt5 import QtCore

from GUI.Controls.Plot import PlotWidget
from GUI.Controls.Plot.Plottables import ImagePlot, ScatterPlot
from GUI.Controls.Plot.Plottables.Annotations import CircleAnnotation
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

from Processing.Utilities.image import smooth_circle_like


class BraggFilterModule(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Bragg'

        # these are the bits used later in the script
        self.fft_im = None
        self.filtersettings = None
        self.new_image_widget = None
        self.fft_plot = None
        self.circ_1 = None
        self.mirror_circ_1 = None
        self.circ_2 = None
        self.circ_middle = None
        self.array_scatter = None
        self.array_radius = None

    def run(self):
        # get the current image
        im = self.active_image_window.image_plot.image_data
        # get the FFT
        self.fft_im = np.fft.fftshift(np.fft.fft2(im, axes=(0, 1)), axes=(0, 1))

        shp = np.array(self.fft_im.shape)

        #
        # Sort out the control widget stuff
        #
        max_radius = math.sqrt(im.shape[0]**2 + im.shape[1]**2) / 2.
        # limits of the position (+- in fft coords)
        max_x = shp[1] / 2
        max_y = shp[0] / 2

        # this is our startin' radius
        r = max_radius / 10
        # our starting position in fft coords
        p_x1 = r * 2
        p_y1 = 0.0

        p_x2 = 0.0
        p_y2 = r * 2

        # our starting position in pixel coords
        p_ix1 = p_x1 + shp[1] / 2
        p_iy1 = p_y1 + shp[0] / 2

        p_ix2 = p_x2 + shp[1] / 2
        p_iy2 = p_y2 + shp[0] / 2

        p_ix_mirror = shp[1] / 2 - p_x1
        p_iy_mirror = p_iy1

        # create parameters for dialog
        x_pos_1 = ['SpinFloat', 0, 'g1 x', (-max_x, max_x, 5.0, p_x1)]
        y_pos_1 = ['SpinFloat', 1, 'g1 y', (-max_y, max_y, 5.0, p_y1)]
        x_pos_2 = ['SpinFloat', 2, 'g2 x', (-max_x, max_x, 5.0, p_x2)]
        y_pos_2 = ['SpinFloat', 3, 'g2 y', (-max_y, max_y, 5.0, p_y2)]
        radius = ['SpinFloat', 4, 'Radius', (0, max_radius, 5.0, r)]
        smooth = ['SpinFloat', 5, 'Smooth', (0, max_radius, 1.0, 5)]

        mirror = ['Check', 6, 'Mirror', True]
        array = ['Check', 7, 'Array', False]


        # runs as modal dlg
        self.filtersettings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            name='High/low pass filter',
            inputs=[x_pos_1, y_pos_1, x_pos_2, y_pos_2, radius, smooth, mirror, array],
            show_preview=True, preserve_image=True)
        self.filtersettings.sigApplyFilter.connect(self.do_bragg)

        self.add_widget_to_image_window(self.filtersettings, 0, 3)

        #
        # Sort out the fft display stuff
        #

        self.new_image_widget = PlotWidget()

        # # show it next to the current image
        self.active_image_window.ui.gridLayout.addWidget(self.new_image_widget, 0, 2)

        self.fft_plot = ImagePlot(self.fft_im)
        self.new_image_widget.plot_view.add_widget(self.fft_plot, fit=True)
        self.new_image_widget.update()

        #
        self.circ_1 = CircleAnnotation(movable=True, resize_symmetric=True, maintain_aspect=True,
                                       fill_colour=np.array([233, 142, 34, 100]) / 255,
                                       border_colour=np.array([233, 142, 34, 255]) / 255,
                                       border_width=2, z_value=999)
        self.circ_1.make_buffers(p_ix1, p_iy1, r, r)

        self.mirror_circ_1 = CircleAnnotation(selectable=False, movable=False,
                                              resize_symmetric=True, maintain_aspect=True,
                                              fill_colour=np.array([255, 255, 255, 100]) / 255,
                                              border_colour=np.array([255, 255, 255, 255]) / 255,
                                              border_width=2, z_value=998)
        self.mirror_circ_1.make_buffers(p_ix_mirror, p_iy_mirror, r, r)

        self.circ_2 = CircleAnnotation(movable=True, resize_symmetric=True, maintain_aspect=True,
                                       fill_colour=np.array([44, 160, 44, 100]) / 255,
                                       border_colour=np.array([44, 160, 44, 255]) / 255,
                                       border_width=2, z_value=999, visible=False)
        self.circ_2.make_buffers(p_ix2, p_iy2, r, r)

        self.circ_middle = CircleAnnotation(movable=False, resize_symmetric=True, maintain_aspect=True,
                                       fill_colour=np.array([214, 39, 40, 100]) / 255,
                                       border_colour=np.array([214, 39, 40, 255]) / 255,
                                       border_width=2, z_value=999, visible=False)
        self.circ_middle.make_buffers(shp[1] / 2, shp[0] / 2, r, r)

        self.array_radius = 10
        # this is the total count, subtract 3 for the 4 circles we have already defined above!
        n = (self.array_radius * 2 + 1)**2 - 4
        points = np.zeros((n, 2), dtype=np.float32)
        self.array_scatter = ScatterPlot(points=points, size=10, border_width=2,
                                         fill_colour=np.array([255, 255, 255, 100]) / 255,
                                         border_colour=np.array([255, 255, 255, 255]) / 255,
                                         visible=False, use_screen_space=False, z_value=998)

        self.new_image_widget.plot_view.add_widget(self.circ_2)
        self.new_image_widget.plot_view.add_widget(self.circ_1)
        self.new_image_widget.plot_view.add_widget(self.mirror_circ_1)
        self.new_image_widget.plot_view.add_widget(self.circ_middle)
        self.new_image_widget.plot_view.add_widget(self.array_scatter)

        self.update_array_circs()

        self.new_image_widget.update()

        self.filtersettings.controls['g2 x'].setEnabled(False)
        self.filtersettings.controls['g2 y'].setEnabled(False)

        # now we need to connect our filter settings widget to the circle annotation
        self.filtersettings.controls['Radius'].valueChanged.connect(self.update_plot_from_box)
        self.filtersettings.controls['g1 x'].valueChanged.connect(self.update_plot_from_box)
        self.filtersettings.controls['g1 y'].valueChanged.connect(self.update_plot_from_box)
        self.filtersettings.controls['g2 x'].valueChanged.connect(self.update_plot_from_box)
        self.filtersettings.controls['g2 y'].valueChanged.connect(self.update_plot_from_box)

        self.filtersettings.controls['Mirror'].stateChanged.connect(self.mirror_toggled)
        self.filtersettings.controls['Array'].stateChanged.connect(self.array_toggled)

        # now we update the textboxes when we move the object
        self.circ_1.signal_changed.connect(self.update_box_from_plot_1)
        self.circ_2.signal_changed.connect(self.update_box_from_plot_2)
        self.circ_middle.signal_changed.connect(self.update_box_from_zero_vector)

        self.filtersettings.signal_result.connect(self.got_result)

    def got_result(self, widget, state):
        # TODO: clear this up properly
        # self.new_image_widget.remove_item(self.circ)
        # self.circ = None

        self.new_image_widget.plot_view.remove_widget(self.fft_plot)
        self.fft_plot.image_data = None
        self.fft_plot = None

        # print('getting rid of')
        self.active_image_window.ui.gridLayout.removeWidget(self.new_image_widget)
        # todo: does this do what I want?? does it ever actually get deleted?
        self.new_image_widget.close()

        self.new_image_widget = None

        self.fft_im = None
        self.filtersettings = None

    def update_plot_from_box(self, val):
        # self.circ_1.set_radius(val)
        # self.new_image_widget.update()
        return

    def mirror_toggled(self, state):
        checked = state == QtCore.Qt.Checked

        mirror_visible = checked or self.filtersettings.controls['Array'].checkState() == QtCore.Qt.Checked
        self.mirror_circ_1.set_visible(mirror_visible)

        self.new_image_widget.update()

    def array_toggled(self, state):
        checked = state == QtCore.Qt.Checked
        self.circ_2.set_visible(checked)
        self.array_scatter.set_visible(checked)

        # TODO: handle mirror circle check being toggled off when it shouldnt be
        mirror_visible = checked or self.filtersettings.controls['Mirror'].checkState() == QtCore.Qt.Checked
        self.mirror_circ_1.set_visible(mirror_visible)

        self.circ_middle.set_visible(checked)

        self.filtersettings.controls['g2 x'].setEnabled(checked)
        self.filtersettings.controls['g2 y'].setEnabled(checked)

        self.new_image_widget.update()

    def update_box_from_plot_1(self, t, l, b, r):
        self.update_box_from_g_vectors(self.circ_1, t, l, b, r)

    def update_box_from_plot_2(self, t, l, b, r):
        self.update_box_from_g_vectors(self.circ_2, t, l, b, r)

    def update_box_from_zero_vector(self, t, l, b, r):
        r_x = (r - l) / 2
        r_y = (t - b) / 2

        self.mirror_circ_1.set_radius(r_x, r_y)
        self.circ_1.set_radius(r_x, r_y, emit=False)
        self.circ_2.set_radius(r_x, r_y, emit=False)
        self.array_scatter.radii = np.array([r_x, r_y], dtype=np.float32) * 2

        # update the textboxes
        self.filtersettings.controls['Radius'].valueChanged.disconnect(self.update_plot_from_box)

        self.filtersettings.controls['Radius'].setValue(r_x)

        self.filtersettings.controls['Radius'].valueChanged.connect(self.update_plot_from_box)

    def update_box_from_g_vectors(self, sender, t, l, b, r):
        if sender == self.circ_1:
            other_circ = self.circ_2
            edt_x = self.filtersettings.controls['g1 x']
            edt_y = self.filtersettings.controls['g1 y']
            # func = self.update_box_from_plot_1
        else:
            other_circ = self.circ_1
            edt_x = self.filtersettings.controls['g2 x']
            edt_y = self.filtersettings.controls['g2 y']
            # func = self.update_box_from_plot_2

        # get the radii from our circle
        r_x = (r - l) / 2
        r_y = (t - b) / 2

        # get the position
        shp = np.array(self.fft_im.shape)
        c_x = (r + l - shp[1]) / 2
        c_y = (t + b - shp[0]) / 2  # could *-1 to get the +- in screen coords?

        # we will need to update the mirror circle (always do this?)
        c_x_mirror = shp[1] / 2 - c_x
        c_y_mirror = shp[0] / 2 - c_y

        # update the mirrored circle
        if sender == self.circ_1:
            self.mirror_circ_1.set_position_radius(c_x_mirror, c_y_mirror, r_x, r_y)
        else:
            self.mirror_circ_1.set_radius(r_x, r_y)

        self.circ_middle.set_radius(r_x, r_y)

        # update the second circle radius
        # emit false to stop recursive updating
        other_circ.set_radius(r_x, r_y, emit=False)

        self.update_array_circs()

        # update the textboxes
        edt_x.valueChanged.disconnect(self.update_plot_from_box)
        edt_y.valueChanged.disconnect(self.update_plot_from_box)
        self.filtersettings.controls['Radius'].valueChanged.disconnect(self.update_plot_from_box)

        edt_x.setValue(c_x)
        edt_y.setValue(c_y)
        self.filtersettings.controls['Radius'].setValue(r_x)

        edt_x.valueChanged.connect(self.update_plot_from_box)
        edt_y.valueChanged.connect(self.update_plot_from_box)
        self.filtersettings.controls['Radius'].valueChanged.connect(self.update_plot_from_box)

    def update_array_circs(self):
        # this is where the array circles are set!
        # first find centre of image
        mid = np.ceil(np.array(self.fft_im.shape)[:2] / 2)
        # TODO: the x/y order of this is incompatible

        # first get the g vectors
        # TODO: should really get these from the textbox? - need to be careful when this function is called
        g_1 = np.array(self.circ_1.get_centre()) - mid
        g_2 = np.array(self.circ_2.get_centre()) - mid
        # and the radii
        r = np.array(self.circ_1.get_radii())

        n = self.array_radius
        nn = (self.array_radius * 2 + 1) ** 2 - 4
        points = np.zeros((nn, 2), dtype=np.float32)
        count = 0
        for i in range(-n, n+1):
            for j in range(-n, n+1):
                # account for the circles we already have
                if (i == 1 and j == 0) or (i == 0 and j == 1) or (i == -1 and j == 0) or (i == 0 and j == 0):
                    continue

                cent = mid + g_1*i + g_2*j

                points[count, :] = cent
                count += 1

        self.array_scatter.set_points(points)
        self.array_scatter.radii = r * 2

    def do_bragg(self, vals):
        # get the radius we have set currently
        r = vals['Radius']
        smth = vals['Smooth'] / 2

        im_shp = np.array(self.fft_im.shape)
        c = np.ceil(im_shp / 2)

        v1 = np.array([vals['g1 y'], vals['g1 x']])

        v2 = np.array([vals['g2 y'], vals['g2 x']])

        do_array = vals['Array']
        do_mirror = vals['Mirror']

        mask = np.zeros_like(self.fft_im, dtype=np.float64)

        #
        # Need to work out our mask array
        #
        if do_array:
            n1_a = np.abs(im_shp[0] / (v1[0] + v2[0]))
            n1_b = np.abs(im_shp[0] / (v1[0] - v2[0]))
            n1_c = np.abs(im_shp[0] / (-v1[0] + v2[0]))

            n2_a = np.abs(im_shp[1] / (v1[1] + v2[1]))
            n2_b = np.abs(im_shp[1] / (v1[1] - v2[1]))
            n2_c = np.abs(im_shp[1] / (-v1[1] + v2[1]))

            n = np.max([n1_a, n1_b, n1_c, n2_a, n2_b, n2_c])
            n = int(np.ceil(n / 2))

            for j in range(-n, n+1):
                for i in range(-n, n + 1):
                    v = j * v1 + i * v2 + c

                    r_eff = r + smth

                    if im_shp[0] + r_eff > v[0] > -r_eff and im_shp[1] + r_eff > v[1] > -r_eff:
                        new_mask = smooth_circle_like(self.fft_im, v[1], v[0], r - smth, r + smth)

                        larger = new_mask > mask
                        mask[larger] = new_mask[larger]
        else:
            new_mask = smooth_circle_like(self.fft_im, c[1] + v1[1], c[0] + v1[0], r - smth, r + smth)
            larger = new_mask > mask
            mask[larger] = new_mask[larger]

        if do_mirror:
            new_mask = smooth_circle_like(self.fft_im, c[1] - v1[1], c[0] - v1[0], r - smth, r + smth)
            larger = new_mask > mask
            mask[larger] = new_mask[larger]

        masked_fft = self.fft_im * mask

        # new_im = np.log(np.abs(masked_fft) + 1)
        new_im = np.real(np.fft.ifft2(np.fft.fftshift(masked_fft)))

        self.create_or_update_image("Image", new_im, keep_view=True)