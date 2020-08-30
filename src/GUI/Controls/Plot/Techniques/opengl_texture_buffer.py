import OpenGL.GL as gl

from .opengl_array_buffer import OglArrayBuffer
import numpy as np


class OglTextureBuffer:
    def __init__(self, buffer_data, unit=0):
        self.width = buffer_data.shape[1]
        self.height = buffer_data.shape[0]

        self.unit = unit

        self.texture = gl.glGenTextures(1)

        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST_MIPMAP_NEAREST)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R32F, self.width, self.height, 0,
                        gl.GL_RED, gl.GL_FLOAT, buffer_data)

        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    def bind(self):
        # if not self.exists():
        #     return

        gl.glActiveTexture(gl.GL_TEXTURE0 + self.unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

    def unbind(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
