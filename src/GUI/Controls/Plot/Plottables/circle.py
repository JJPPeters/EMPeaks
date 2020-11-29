import numpy as np

from GUI.Controls.Plot.Techniques import OglCircleTechnique


class Circle(OglCircleTechnique):
    def __init__(self, centre=None, radii=None, fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), border_width=2, z_value=1, visible=True):
        super(Circle, self).__init__(fill_colour=fill_colour,
                                     border_colour=border_colour,
                                     border_width=border_width,
                                     z_value=z_value,
                                     visible=visible)

        if centre is not None and radii is not None:
            self.set_data(centre[0], centre[1], radii[0], radii[1])

    def set_data(self, c_x, c_y, r_x, r_y):
        self.make_buffers(c_x, c_y, r_x, r_y)
