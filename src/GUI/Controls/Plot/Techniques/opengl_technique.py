import sys
import math

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

import OpenGL.GL as gl
from .opengl_error import have_valid_context


class OglTechnique:
    def __init__(self):
        self._parent = None

        self.shader_program = None
        self.shader_objects = []

        self.model_view_location = None
        self.projection_location = None
        self.model_view_projection_location = None

        self.visible = True

    @property
    def parent(self: QOpenGLWidget):
        return self._parent

    @parent.setter
    def parent(self, p: QOpenGLWidget):
        if p is None:
            return
        self._parent = p

        if self._parent.isValid():
            p.makeCurrent()
            self.initialise()

    def delete(self):
        if not have_valid_context():
            return

        for obj in self.shader_objects:
            try:
                gl.glDeleteShader(obj)
            except gl.OpenGL.error.GLerror as e:
                print("deleting shader badly? shader")
                print(str(e))

        self.shader_objects.clear()

        if self.shader_program is not None and self.shader_program != 0:
            try:
                gl.glDeleteProgram(self.shader_program)
            except gl.OpenGL.error.GLerror as e:
                print("deleting program badly? shader")
                print(str(e))

        self.shader_program = 0

    def on_click(self, pos_x, pos_y, ratio):
        return None

    def initialise(self):
        if self.parent is None:
            raise Exception("Initialising technique without context")

        self.parent.makeCurrent()

        self.shader_program = gl.glCreateProgram()
        if self.shader_program == -1:
            raise Exception("Could not create shader program")

    def finalise(self):
        gl.glLinkProgram(self.shader_program)
        success = gl.glGetProgramiv(self.shader_program, gl.GL_LINK_STATUS)

        if not success:
            message = gl.glGetProgramInfoLog(self.shader_program)
            raise Exception("Could not get program: " + message.decode("utf-8"))

        gl.glValidateProgram(self.shader_program)
        success = gl.glGetProgramiv(self.shader_program, gl.GL_VALIDATE_STATUS)

        if not success:
            message = gl.glGetProgramInfoLog(self.shader_program)
            raise Exception("Could not get program: " + message.decode("utf-8"))

    def enable(self):
        if self.shader_program is not None:
            try:
                gl.glUseProgram(self.shader_program)
            except gl.OpenGL.error.GLError as e:
                print('Trying to use dodgy program?')
                print(e)

    def disable(self):
        gl.glUseProgram(0)

    def get_uniform_location(self, uniform_name):
        location = gl.glGetUniformLocation(self.shader_program, uniform_name)

        if location == -1:
            raise Exception("Could not find uniform location: " + uniform_name)

        return location

    def get_program_param(self, param_name):
        param = gl.glGetProgramiv(self.shader_program, param_name)
        return param

    def get_attribute_location(self, attribute_name):
        location = gl.glGetAttribLocation(self.shader_program, attribute_name)

        if location == -1:
            raise Exception("Could not find attribute location: " + attribute_name)

        return location

    def compile_shader(self, shader_type, shader_string):
        shader_object = gl.glCreateShader(shader_type)

        if shader_object == 0:
            raise Exception("Could not create shader")

        gl.glShaderSource(shader_object, shader_string)

        gl.glCompileShader(shader_object)

        success = gl.glGetShaderiv(shader_object, gl.GL_COMPILE_STATUS)

        if not success:
            message = gl.glGetShaderInfoLog(shader_object)
            raise Exception(message)

        gl.glAttachShader(self.shader_program, shader_object)

        self.shader_objects.append(shader_object)

    def set_model_view(self, model_view):
        gl.glUniformMatrix4fv(self.model_view_location, 1, gl.GL_TRUE, model_view)

    def set_projection(self, projection):
        gl.glUniformMatrix4fv(self.projection_location, 1, gl.GL_TRUE, projection)

    def set_model_view_projection(self, model_view):
        gl.glUniformMatrix4fv(self.model_view_projection_location, 1, gl.GL_TRUE, model_view)