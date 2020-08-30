from PyQt5 import QtGui, QtCore
import numpy as np

from GUI.Controls.Plot.Techniques import OglNumberTextTechnique, HorizontalAlign, VerticalAlign

from PyQt5.QtWidgets import QOpenGLWidget

from GUI.Controls.Plot.Techniques.opengl_error import GlBufferError


class NumberTextPlot(OglNumberTextTechnique, QtCore.QObject):
    def __init__(self, text=None, position=None, position_y=None, font_size=10, horizontal_align=HorizontalAlign.Left, vertical_align=VerticalAlign.Baseline, colour=None, z_value=1, visible=True):
        super(NumberTextPlot, self).__init__(horizontal_align=horizontal_align, vertical_align=vertical_align, z_value=z_value, visible=visible)

        self.parent = None
        self.fontsize = font_size

        if text is not None:
            self.set_text(text)

        if position is not None:
            self.set_position(position, position_y)

    def _do_make_buffers(self):
        if self.origin is not None:
            self.make_buffers(self.origin, self.text, self.fontsize)

    def set_text(self, text: str):
        self.text = text
        self.align_offset = self.calculate_align_offset()

    def set_position(self, x, y=None):
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

            x = np.hstack((y, x))

        self.origin = x
        try:
            self.make_buffers(self.origin, self.text, self.fontsize)
        except GlBufferError:
            return

    def number_to_superscript(self, number: str):
        out = ""

        for c in number:
            if c == "0":
                out += "⁰"
            elif c == "1":
                out += "¹"
            elif c == "2":
                out += "²"
            elif c == "3":
                out += "³"
            elif c == "4":
                out += "⁴"
            elif c == "5":
                out += "⁵"
            elif c == "6":
                out += "⁶"
            elif c == "7":
                out += "⁷"
            elif c == "8":
                out += "⁸"
            elif c == "9":
                out += "⁹"
            elif c == "+":
                out += "⁺"
            elif c == "-":
                out += "⁻"

        return out