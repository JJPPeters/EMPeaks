import numpy as np

from GUI.Controls.Plot.Techniques import OglPolarImageTechnique

from GUI.Utilities.enums import ImageType, WindowType, AnnotationType, ComplexDisplay
# from GUI.Controls.Plot import PlotWidget


class PolarImagePlot(OglPolarImageTechnique):
    def __init__(self, angle=None, magnitude=None, alpha=None,
                 pixel_scale: float = 1.0,
                 origin=np.array([0.0, 0.0], dtype=np.float32),
                 z_value=1, visible=True):
        super(PolarImagePlot, self).__init__(pixel_scale=pixel_scale,
                                             origin=origin,
                                             z_value=z_value, visible=visible)

        self.plot_type = AnnotationType.Polar

        self.parent = None

        self.angle_data = None
        self.magnitude_data = None
        self.alpha_data = None

        self.angle_offset = 0

        self.colour_map = None

        self.cmap_angle_offset = 0.0

        # for intensity display
        self.limitsHistory = [(0., 1.)]

        # this is used to set the brightness, contrast and gamma of the image
        self.BCG = np.array([0.5, 0.5, 0.5])

        # self.current_slice = 0

        self.initialise()

        self.set_data(angle, magnitude, alpha)

    @property
    def slices(self):
        return 1

    def update_display(self):
        if self.parent is not None:
            self.parent.makeCurrent()

        self.make_buffers(self.angle_data, self.magnitude_data, self.alpha_data)

        if self.parent is not None:
            self.parent.update()

    def set_data(self, angle, magnitude, alpha, update=True, keep_view=False):
        self.angle_data = angle
        self.magnitude_data = magnitude
        self.alpha_data = alpha
        if self.angle_data is not None and self.magnitude_data is not None and update:
            self.update_display()

    def set_colour_map(self, col_map):
        self.colour_map = col_map
        super(PolarImagePlot, self).set_colour_map(col_map)
        if self.parent is not None:
            self.parent.update()

    def set_cmap_angle_offset(self, angle):
        self.cmap_angle_offset = angle
        super(PolarImagePlot, self).set_cmap_angle_offset(angle)
        if self.parent is not None:
            self.parent.update()

    def set_bcg(self, b, c, g):
        self.BCG = np.array([b, c, g])
        super(PolarImagePlot, self).set_bcg(b, c, g)
        if self.parent is not None:
            self.parent.update()

    def set_levels(self, levels):
        super(PolarImagePlot, self).set_levels(levels)
        if self.parent is not None:
            self.parent.update()
