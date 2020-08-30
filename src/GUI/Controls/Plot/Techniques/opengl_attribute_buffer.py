import OpenGL.GL as gl
import numpy as np

from .opengl_array_buffer import OglArrayBuffer
import ctypes

class OglAttributeBuffer(OglArrayBuffer):
    def __init__(self, buffer_data, buffer_location, buffer_type=gl.GL_ARRAY_BUFFER):
        super(OglAttributeBuffer, self).__init__(buffer_data, buffer_type)

        self.type = buffer_data.dtype

        self.buffer_location = buffer_location
        self.stride = 0
        self.offset = 0

    def bind(self):
        if not self.exists():
            return

        gl.glEnableVertexAttribArray(self.buffer_location)
        gl.glBindBuffer(self.buffer_type, self.buffer)

        if self.type == np.float32:
            gl.glVertexAttribPointer(self.buffer_location, self.size_per, gl.GL_FLOAT, gl.GL_FALSE, 4 * self.stride,
                                     ctypes.c_void_p(4 * self.offset))   # in C++, final element was the buffer object?
        elif self.type == np.int32:
            gl.glVertexAttribPointer(self.buffer_location, self.size_per, gl.GL_INT, gl.GL_FALSE, 4 * self.stride,
                                     ctypes.c_void_p(4 * self.offset))

    def unbind(self):
        if not self.exists():
            return

        gl.glBindBuffer(self.buffer_type, 0)
        gl.glDisableVertexAttribArray(self.buffer_location)
