from GUI.Modules.menu_entry_module import MenuEntryModule
import numpy as np
import math

from GUI.Controls.Plot import PlotWidget
from GUI.Controls.Plot.Plottables import ImagePlot
from GUI.Controls.Plot.Plottables.Annotations import RingAnnotation
from GUI.Controls.ProcessSettingsFrame import ProcessSettingsFrame

from Processing.Utilities.image import smooth_circle_like


class BandPass(MenuEntryModule):
    def __init__(self):
        super().__init__()
        self.menu_structure = ['Image', 'Filter']
        self.name = 'Band pass'

        # these are the bits used later in the script
        self.fft_im = None
        self.filtersettings = None
        self.new_image_widget = None
        self.fft_plot = None
        self.ring = None

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
        r = shp / 5

        # create parameters for dialog
        in_r = ['SpinFloat', 0, 'Inner radius', (0, r[1], 5.0, r[1] / 2)]
        out_r = ['SpinFloat', 1, 'Outer radius', (r[1] / 2, max_radius, 5.0, r[1])]
        smooth = ['SpinFloat', 2, 'Smooth', (0, max_radius, 1.0, 5)]

        # runs as modal dlg
        self.filtersettings = ProcessSettingsFrame(
            master=self.main_window.last_active,
            function=self.do_band_pass,
            name='Band pass filter',
            inputs=[in_r, out_r, smooth],
            show_preview=True, preserve_image=True)

        self.add_widget_to_image_window(self.filtersettings, 0, 3)

        #
        # Sort out the fft display stuff
        #

        self.new_image_widget = PlotWidget()

        # # show it next to the current image
        self.active_image_window.ui.gridLayout.addWidget(self.new_image_widget, 0, 2)

        self.fft_plot = ImagePlot(self.fft_im)
        self.new_image_widget.add_item(self.fft_plot, fit=True)
        self.new_image_widget.update()

        # get the centre of the FFT (and a arbitrary radius that is within the image
        c = np.ceil(shp / 2)

        self.ring = RingAnnotation(movable=False, resize_symmetric=True, maintain_aspect=True,
                                   fill_colour=np.array([233, 142, 34, 100]) / 255,
                                   border_colour=np.array([233, 142, 34, 255]) / 255,
                                   border_width=2, z_value=999)
        self.ring.make_buffers(c[1], c[0], r[1], r[0], 0.5)

        self.new_image_widget.add_item(self.ring)
        self.new_image_widget.update()

        # now we need to connect our filter settings widget to the circle annotation
        self.filtersettings.controls['Inner radius'].valueChanged.connect(self.update_plot_from_box)
        self.filtersettings.controls['Outer radius'].valueChanged.connect(self.update_plot_from_box)
        self.ring.signal_ring_changed.connect(self.update_box_from_plot)

        self.filtersettings.signal_result.connect(self.got_result)

    def got_result(self, widget, state):
        self.new_image_widget.remove_item(self.ring)
        self.ring = None

        self.new_image_widget.remove_item(self.fft_plot)
        self.fft_plot.image_data = None
        self.fft_plot = None

        print('getting rid of')
        self.active_image_window.ui.gridLayout.removeWidget(self.new_image_widget)
        # todo: does this do what I want?? does it ever actually get deleted?
        self.new_image_widget.close()

        self.new_image_widget = None

        self.fft_im = None
        self.filtersettings = None

    def update_plot_from_box(self, val):
        in_r = self.filtersettings.controls['Inner radius'].value()
        out_r = self.filtersettings.controls['Outer radius'].value()
        
        # Update the new min/max values
        self.filtersettings.controls['Inner radius'].setMaximum(out_r - 1)
        self.filtersettings.controls['Outer radius'].setMinimum(in_r + 1)

        self.ring.set_radius_inner_fraction(out_r, frac=in_r / out_r)
        self.new_image_widget.update()

    def update_box_from_plot(self, t, l, b, r, in_frac):
        r_out_x = (r - l) / 2
        r_in_x = r_out_x * in_frac
        # r_y = (t - b) / 2

        # disconnect these slots so that we don't get a recursive loop of plot updates textbox that updates plot etc...
        self.filtersettings.controls['Inner radius'].valueChanged.disconnect(self.update_plot_from_box)
        self.filtersettings.controls['Outer radius'].valueChanged.disconnect(self.update_plot_from_box)

        self.filtersettings.controls['Inner radius'].setMaximum(r_out_x - 1)
        self.filtersettings.controls['Outer radius'].setMinimum(r_in_x + 1)

        self.filtersettings.controls['Inner radius'].setValue(r_in_x)
        self.filtersettings.controls['Outer radius'].setValue(r_out_x)

        self.filtersettings.controls['Inner radius'].valueChanged.connect(self.update_plot_from_box)
        self.filtersettings.controls['Outer radius'].valueChanged.connect(self.update_plot_from_box)

    def do_band_pass(self, vals):
        # get the radius we have set currently
        r_in = vals['Inner radius']
        r_out = vals['Outer radius']
        smth = vals['Smooth'] / 2

        c = np.ceil(np.array(self.fft_im.shape) / 2)
        mask_outer = smooth_circle_like(self.fft_im, c[1], c[0], r_out - smth, r_out + smth)
        mask_inner = smooth_circle_like(self.fft_im, c[1], c[0], r_in - smth, r_in + smth)

        mask = mask_inner - mask_outer

        masked_fft = self.fft_im * mask
        new_im = np.abs(np.fft.ifft2(np.fft.fftshift(masked_fft)))

        self.create_or_update_image("Image", new_im, keep_view=True)