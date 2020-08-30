import OpenGL.GL as gl

from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtGui import QColor, QOpenGLVertexArrayObject, QOpenGLContext
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QOpenGLWidget, QSlider, QWidget


class GlBufferError(Exception):
    pass

def have_valid_context():
    return QOpenGLContext.currentContext() is not None

# def check_errors():
#
#     message = ""
#
#     error = gl.glGetError()
#
#     while error != gl.GL_NO_ERROR:
#         error = gl.glGetError()
#
#         message +=
