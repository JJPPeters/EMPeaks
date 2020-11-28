import sys
import math

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor, QOpenGLVertexArrayObject
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

import OpenGL.GL as gl
import numpy as np

import scipy.misc

from .opengl_camera import OglCamera

from .opengl_framebuffer import OglFramebuffer

import os

# raw example taken from: https://raw.githubusercontent.com/baoboa/pyqt5/master/examples/opengl/hellogl.py


class GLPlotWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLPlotWidget, self).__init__(parent)

        self.background_colour = np.array([50, 0, 50, 255], dtype=np.float32) / 255

        self.vao = None
        self.framebuffer = None

        self.plot_camera = OglCamera(invert_y=False)
        self.plot_camera.set_projection_limits(1, 0, 0, 1)

        # https://stackoverflow.com/questions/37303941/qt5-6-high-dpi-support-and-opengl-openscenegraph
        # TODO: this needs to update as the window moves across screens
        screen_id = QApplication.desktop().screenNumber(self)
        screen = QApplication.desktop().screen(screen_id)
        # pixels per inch or payment protection insurance?
        # ppi = screen.physicalDotsPerInch()
        self.plot_camera.pixel_ratio = screen.devicePixelRatio()

        self.techniques = []

    # def delete(self):
    #     try:
    #         self.makeCurrent()
    #         self.framebuffer = None
    #         self.doneCurrent()
    #     except RuntimeError:
    #         return

    def initializeGL(self):

        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        gl.glClearColor(*self.background_colour)
        gl.glClearDepth(0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        #  https://learnopengl.com/Advanced-OpenGL/Blending
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # gl.glBlendFuncSeparate(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA, gl.GL_ZERO, gl.GL_ONE)

        # these aren't needed in our 2d world
        # gl.glEnable(gl.GL_CULL_FACE)
        # gl.glCullFace(gl.GL_BACK)
        # gl.glFrontFace(gl.GL_CW)

        gl.glEnable(gl.GL_MULTISAMPLE)
        gl.glEnable(gl.GL_SAMPLE_SHADING)
        gl.glMinSampleShading(1.0)

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_GEQUAL)
        # gl.glDepthMask(gl.GL_FALSE)  # enabled by default

        self.framebuffer = OglFramebuffer(self.width(), self.height(), scaling=self.plot_camera.pixel_ratio, multisample=4)
        self.framebuffer.resize(self.width(), self.height())

        for technique in self.techniques:
            technique.initialise()

        if gl.glGetError() != gl.GL_NO_ERROR:
            print("OOPS")

    def paintGL(self):

        default_framebuffer = gl.glGetIntegerv(gl.GL_DRAW_FRAMEBUFFER_BINDING)

        gl.glBindVertexArray(self.vao)

        self.framebuffer.bind()

        gl.glClearColor(*self.background_colour)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        projection = self.plot_camera.get_projection_matrix()

        # these ratios should be the same for a pixel aspect ratio of 1
        # they effectively act as an screen pixel scale to view/image scale
        ratio_x = self.width() / (self.plot_camera.projection_edges[3] - self.plot_camera.projection_edges[1])
        ratio_y = self.height() / (self.plot_camera.projection_edges[0] - self.plot_camera.projection_edges[2])
        ratio = (ratio_x, ratio_y)

        pr = self.plot_camera.pixel_ratio

        for technique in self.techniques:
            technique.render(projection, pr*self.width(), pr*self.height(), ratio)

        self.framebuffer.blit(default_framebuffer)

        self.framebuffer.unbind()

    def resizeGL(self, w, h):
        self.plot_camera.set_projection_limits(h, 0, 0, w)
        self.framebuffer.resize(w, h, scaling=self.plot_camera.pixel_ratio)

    def add_item(self, item, index=None):
        item.parent = self

        if self.isValid():
            item.initialise()

        if index is None:
            self.techniques.append(item)
            self.techniques.sort(key=lambda x: x.z_value)  # this is important for rendering transparancy
        else:
            self.techniques.insert(index, item)
