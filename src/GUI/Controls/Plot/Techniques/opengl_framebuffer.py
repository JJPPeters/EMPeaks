import OpenGL.GL as gl

from .opengl_attribute_buffer import OglAttributeBuffer
from PyQt5.QtGui import QOpenGLVertexArrayObject

from .opengl_technique import OglTechnique
import numpy as np
from .opengl_error import have_valid_context

# I really found this useful (and that entire website): https://learnopengl.com/Advanced-OpenGL/Anti-Aliasing
class OglFramebuffer(OglTechnique):
    def __init__(self, width, height, scaling=1.0, multisample=1):
        super(OglFramebuffer, self).__init__()

        # these get set by the resize method
        self.width = None
        self.height = None
        self.scaling = None

        self.multisample = int(multisample)

        self.fbo = gl.glGenFramebuffers(1)
        self.rbo_c = gl.glGenRenderbuffers(1)
        self.rbo_d = gl.glGenRenderbuffers(1)

        self.resize(width, height, scaling)

    def delete(self):
        if not have_valid_context():
            return

        if gl.glIsFramebuffer(self.fbo):
            gl.glDeleteFramebuffers(1, [self.fbo])
        self.fbo = -1

        if gl.glIsRenderbuffer(self.rbo_c):
            gl.glDeleteRenderbuffers(1, [self.rbo_c])
        self.rbo_c = -1

        if gl.glIsRenderbuffer(self.rbo_d):
            gl.glDeleteRenderbuffers(1, [self.rbo_d])
        self.rbo_d = -1

    def resize(self, width, height, scaling=1.0):
        self.width = int(width * scaling)
        self.height = int(height * scaling)
        self.scaling = scaling
        self.bind()

        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.rbo_c)
        if self.multisample > 1:
            gl.glRenderbufferStorageMultisample(gl.GL_RENDERBUFFER, self.multisample, gl.GL_RGB, self.width, self.height)
        else:
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_RGB, self.width, self.height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_RENDERBUFFER, self.rbo_c)

        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.rbo_d)
        if self.multisample > 1:
            gl.glRenderbufferStorageMultisample(gl.GL_RENDERBUFFER, self.multisample, gl.GL_DEPTH24_STENCIL8, self.width, self.height)
        else:
            gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, self.width, self.height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT, gl.GL_RENDERBUFFER, self.rbo_d)

        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Could not bind framebuffer. Error: " + str(status))

        self.unbind()

    def bind(self):
        if self.fbo >= 0:
            try:
                gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fbo)
            except:
                print("fbo not valid or something?")
        else:
            print("fbo not in valid range...")

    def unbind(self):
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def blit(self, destination_buffer):
        try:
            gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.fbo)
        except gl.OpenGL.error.GLError as e:
            print("fbo fucked up 2")
            print(str(e))
            return
        try:
            gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, destination_buffer)
        except gl.OpenGL.error.GLError as e:
            print("fbo fucked up 3")
            print(str(e))
            return
        gl.glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, self.width, self.height,
                             gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT | gl.GL_STENCIL_BUFFER_BIT, gl.GL_NEAREST)
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, 0)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)

    def read_data(self):
        self.bind()

        pixel_buffer = gl.glReadPixels(0, 0, self.width, self.height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)

        self.unbind()

        rgb_image = np.fromstring(pixel_buffer, "uint8", count=self.width * self.height * 4)
        return np.flip(rgb_image.reshape((self.height, self.width, 4)), 0)
