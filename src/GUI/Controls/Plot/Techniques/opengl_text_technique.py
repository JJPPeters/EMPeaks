import OpenGL.GL as gl
from scipy import ndimage

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .opengl_texture_buffer import OglTextureBuffer
from .shaders import text_shader as shaders
from .opengl_error import GlBufferError

from PIL import ImageFont

import numpy as np

class OglTextTechnique(OglTechnique):

    def __init__(self, z_value=1, visible=True):
        super(OglTextTechnique, self).__init__()

        self.position_buffer_location = None
        self.texture_unit_location = None
        self.offsets_location = None
        self.z_location = None
        self.model_location = None

        self.width_location = None
        self.height_location = None

        self.image_buffer = None
        self.position_buffer = None

        #
        #
        #

        self.offsets = None

        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        self.visible = visible

        self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

        self.text = None
        self.fontsize = None
        self.origin = None
        self.rotation = 0
        self.model_matrix = np.identity(4)

        self.deferred_make_buffer = None

    def set_rotation(self, r_deg):
        self.rotation = r_deg
        r_rad = np.deg2rad(r_deg)
        self.model_matrix = np.array([[np.cos(r_rad), -np.sin(r_rad), 0.0, 0.0],
                                      [np.sin(r_rad), np.cos(r_rad),  0.0, 0.0],
                                      [0.0,           0.0,            1.0, 0.0],
                                      [0.0,           0.0,            0.0, 1.0]], dtype=np.float32)

    def initialise(self):
        super(OglTextTechnique, self).initialise()

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        geometry_shader_string = shaders.geometry_shader
        self.compile_shader(gl.GL_GEOMETRY_SHADER, geometry_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.offsets_location = self.get_uniform_location("offsets")
        self.projection_location = self.get_uniform_location("projection")
        self.z_location = self.get_uniform_location("z_value")
        self.texture_unit_location = self.get_uniform_location("tex_unit")
        self.model_location = self.get_uniform_location("model")

        self.width_location = self.get_uniform_location("width")
        self.height_location = self.get_uniform_location("height")

        self.position_buffer_location = self.get_attribute_location("text_origin")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, origin, text: str, fontsize=10):
        flag_update_text = True
        if text == self.text and fontsize == self.fontsize and self.image_buffer is not None:
            flag_update_text = False
        self.text = text
        self.fontsize = fontsize
        self.origin = origin.reshape(-1, 2).astype(np.float32)

        try:
            self._make_buffers(update_text=flag_update_text)
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self, update_text=True):
        self._make_position_buffers()
        if update_text:
            self._make_text_buffers()

    def _make_text_buffers(self):
        # https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pil-imagefont
        fnt = ImageFont.truetype("arial.ttf", self.fontsize)
        msk = fnt.getmask(self.text, mode='1')
        ascent, descent = fnt.getmetrics()
        off_y = fnt.getoffset(self.text)[1]
        off_x = msk.size[0] / 2  # this is centered
        text_bitmap = np.asarray(msk).reshape(msk.size[1], msk.size[0])
        text_bitmap = text_bitmap / text_bitmap.max()

        ascent = ascent - off_y - 1
        # old_descent = descent
        descent = text_bitmap.shape[0] - ascent

        self.offsets = np.array([ascent, -off_x, -descent, off_x], dtype=np.float32)

        self.image_buffer = OglTextureBuffer(text_bitmap.astype(np.float32))

    def _make_position_buffers(self):
        if self.position_buffer_location is None:
            raise GlBufferError("Buffer positions are invalid")

        if self.position_buffer is not None:
            self.position_buffer.update_all(self.origin)
        else:
            self.position_buffer = OglAttributeBuffer(self.origin.astype(np.float32), self.position_buffer_location)

    def render(self, projection, width, height, ratio):
        if not self.visible:
            return

        if self.image_buffer is None or self.position_buffer is None:
            return

        self.enable()

        self.set_projection(projection)
        gl.glUniformMatrix4fv(self.model_location, 1, gl.GL_TRUE, self.model_matrix)

        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform4fv(self.offsets_location, 1, self.offsets)

        gl.glUniform1f(self.width_location, width)
        gl.glUniform1f(self.height_location, height)
        gl.glUniform1i(self.texture_unit_location, 0)

        self.image_buffer.bind()
        self.position_buffer.bind()

        gl.glDrawArrays(gl.GL_POINTS, 0, self.position_buffer.size)

        self.position_buffer.unbind()
        self.image_buffer.unbind()

        self.disable()
