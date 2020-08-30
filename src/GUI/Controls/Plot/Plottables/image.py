import numpy as np

from GUI.Controls.Plot.Techniques import OglImageTechnique

from GUI.Utilities.enums import ImageType, WindowType, AnnotationType, ComplexDisplay
# from GUI.Controls.Plot import PlotWidget


class ImagePlot(OglImageTechnique):
    def __init__(self, image=None, z_value=1, visible=True):
        super(ImagePlot, self).__init__(z_value=z_value, visible=visible)

        self.plot_type = AnnotationType.Image

        self.parent = None

        # holds the actual image data
        self.image_data = None
        # if the image is complex, how do we display it
        self.complex_display = None
        # this provides the contrast limits (and a history so we can 'undo' it)
        self.limitsHistory = [(0., 1.)]
        # this is used to set the brightness, contrast and gamma of the image
        self.BCG = [0.5, 0.5, 0.5]
        # this is the name of the colour map!
        self.colour_map = None


        self.current_slice = 0

        self.initialise()

        self.set_data(image)

    @property
    def is_complex(self):
        return np.any(np.iscomplex(self.image_data))

    @property
    def intensities(self):
        if self.image_data.ndim == 3:
            data = self.image_data[:, :, self.current_slice]
        else:
            data = self.image_data

        if not self.is_complex:
            return data

        # now the complex stuff
        if self.complex_display is None:
            raise Exception("Trying to get display intensities of complex image when no display type has been set")
        elif self.complex_display is ComplexDisplay.Real:
            return np.real(data)
        elif self.complex_display is ComplexDisplay.Imaginary:
            return np.imag(data)
        elif self.complex_display is ComplexDisplay.Amplitude:
            return np.abs(data)
        elif self.complex_display is ComplexDisplay.Phase:
            return np.angle(data)
        elif self.complex_display is ComplexDisplay.PowerSpectrum:
            return np.log(np.absolute(data) + 1)

    @property
    def slices(self):
        try:
            return self.image_data.shape[2]
        except IndexError:  # a.k.a the image is 2D
            return 1
        except AttributeError:  # a.k.a this is not a numpy array
            return 0

    def update_display(self):
        self.make_buffers(self.intensities)

        if self.parent is not None:
            self.parent.update()

    def set_data(self, image, update=True, keep_view=False):
        self.image_data = image
        if self.complex_display is None and np.any(np.iscomplex(image)):
            self.complex_display = ComplexDisplay.PowerSpectrum
        if self.image_data is not None and update:
            self.update_display()

    def set_slice(self, index):
        if 0 > index >= self.slices:
            raise Exception("Setting slice out of range: {0}(valid range is {1} to {2})".format(str(index), str(0), str(self.slices)))

        self.current_slice = index
        self.update_display()

    def set_complex_type(self, complex_type):
        if complex_type != self.complex_display:
            self.complex_display = complex_type
            self.update_display()

    def set_colour_map(self, col_map):
        self.colour_map = col_map
        super(ImagePlot, self).set_colour_map(col_map)
        if self.parent is not None:
            self.parent.update()

    def set_levels(self, levels):
        super(ImagePlot, self).set_levels(levels)
        if self.parent is not None:
            self.parent.update()