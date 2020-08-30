import OpenGL.GL as gl
import numpy as np


class OglArrayBuffer:
    def __init__(self, buffer_data, buffer_type=gl.GL_ARRAY_BUFFER):
        self.buffer_type = buffer_type
        self.size = buffer_data.shape[0]
        self.size_per = buffer_data.shape[1]  # I think this is elements per item (i.e. xyz or just xy)
        self.dtype = buffer_data.dtype

        self.buffer = gl.glGenBuffers(1)

        # check buffer pointer is good?

        gl.glBindBuffer(self.buffer_type, self.buffer)
        gl.glBufferData(self.buffer_type, buffer_data, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(self.buffer_type, 0)

    def update_all(self, data):

        # TODO: maybe some test to check the new size is less than the old one
        if self.size * self.size_per < data.size:
            raise Warning("Updating buffer with more data than it can handle")

        # TODO: Might need to check that dtype is the same (or at least the same bytes) - I ran into this error before

        gl.glBindBuffer(self.buffer_type, self.buffer)
        gl.glBufferSubData(self.buffer_type, 0, data.astype(self.dtype))

    def update_single(self, ind, data):
        # TODO: maybe some test to check the new size is less than the old one
        gl.glBindBuffer(self.buffer_type, self.buffer)

        gl.glBufferSubData(self.buffer_type, ind, data)

    def update_list(self, inds, data):
        # TODO: maybe some test to check the new size is less than the old one
        gl.glBindBuffer(self.buffer_type, self.buffer)
        for i in range(inds.size):
            gl.glBufferSubData(self.buffer_type, inds[i], np.array(data[i]))

    def exists(self):
        return self.buffer is not None  # TODO: is this correct (see what glgenbuffers returns..)

    def delete(self):
        # in c++ version, had to check if the context still existed?

        if self.exists():
            gl.glDeleteBuffers(1, self.buffer)
