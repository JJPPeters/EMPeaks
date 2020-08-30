from PyQt5 import QtGui, QtCore
import numpy as np
import numbers

from GUI.Controls.Plot.Techniques import OglTextTechnique

from PyQt5.QtWidgets import QOpenGLWidget

from GUI.Controls.Plot.Techniques.opengl_error import GlBufferError


class TextPlot(OglTextTechnique, QtCore.QObject):
    def __init__(self, text=None, position=None, position_y=None, fontsize=10, colour=None, z_value=1, visible=True):
        super(TextPlot, self).__init__(z_value=z_value, visible=visible)
        # OglTextTechnique.__init__(self, z_value=z_value, visible=visible)
        # QtCore.QObject.__init__(self)

        self.parent = None
        self.points = None

        if position is not None:
            self.set_position(position, position_y, False)

        if text is not None:
            self.set_text(text)

        if self.origin is not None:
            self.make_buffers(self.origin, self.text, fontsize)

    def set_text(self, text: str):
        self.text = text

    def set_position(self, x, y=None, update=True):
        if y is None:
            if x.ndim == 1 and x.size == 2:
                x = x.reshape(-1, 2)

            if x.ndim != 2 or x.shape[0] < 1 or x.shape[1] != 2:
                raise Exception("Trying to plot points with incorrect dimensions")
        else:
            x = np.array(x)
            y = np.array(y)

            if x.size != y.size:
                raise Exception("Trying to plot points with incorrect dimensions")

            x = x.reshape(1, -1)
            y = y.reshape(1, -1)

            x = np.hstack((y, x)).astype(np.float32)

        self.origin = x
        try:
            self._make_position_buffers()
        except GlBufferError:
            return