import numpy as np

from GUI.Controls.Plot.Techniques import OglScatterTechnique
from GUI.Controls.Plot.Techniques import OglRectangleTechnique


class RectAnnotation:
    def __init__(self, view):
        self.handle_colour = np.array([[100, 255, 0, 255]], dtype=np.float32) / 255
        self.roi_fill_colour = np.array([[0, 255, 100, 255]], dtype=np.float32) / 255
        self.roi_border_colour = np.array([[0, 255, 100, 127]], dtype=np.float32) / 255

        self._view = view
        self._visible = True

        #
        # The corners use for selecting the rectangle
        #
        self.roi_handles = []
        for i in range(4):
            s = OglScatterTechnique(size=15, border_width=0, fill_colour=self.handle_colour, z_value=999, visible=False)
            s.initialise()
            s.make_buffers(np.array([0, 0]).reshape((1, 2)))
            self.roi_handles.append(s)

            self._view.add_item(s)

        self.roi_rect = OglRectangleTechnique(fill_colour=self.roi_fill_colour, border_colour=self.roi_border_colour, z_value=998)
        self.roi_rect.initialise()
        self.roi_rect.make_buffers(0, 0, 0, 0)

        self._view.add_item(self.roi_rect)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        for w in self.roi_handles:
            w.visible = value

        self.roi_rect.visible = value

