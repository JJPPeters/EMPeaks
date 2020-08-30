import OpenGL.GL as gl

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .opengl_texture_buffer import OglTextureBuffer
from .shaders import text_shader as shaders
from .opengl_error import GlBufferError

from PIL import ImageFont
from enum import Enum

import numpy as np

class char_info:
    def __init__(self):
        self.offset = 0

class HorizontalAlign(Enum):
    Centre = 0
    Left = 1
    Right = 2

class VerticalAlign(Enum):
    Baseline = 0
    Middle = 1
    Top = 2
    Bottom = 3

class OglNumberTextTechnique(OglTechnique):

    def __init__(self, horizontal_align=HorizontalAlign.Left, vertical_align=VerticalAlign.Baseline, z_value=1, visible=True):
        super(OglNumberTextTechnique, self).__init__()

        self.position_buffer_location = None
        self.texture_unit_location = None
        self.offsets_location = None
        self.z_location = None
        self.model_location = None

        self.width_location = None
        self.height_location = None

        self.glyph_buffers = {}
        self.position_buffer = None

        #
        #
        #

        # self.offsets = None

        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        self.visible = visible

        self.text = None
        self.fontsize = None
        self.origin = None
        self.rotation = 0
        self.model_matrix = np.identity(4, dtype=np.float32)

        self.vert_align = vertical_align
        self.horz_align = horizontal_align
        self.align_offset = self.calculate_align_offset()

        self.glyph_text = "0123456789.-+/()×ⁱ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
        self.glyph_offsets = {}

        self.deferred_make_buffer = None

    def set_rotation(self, r_deg):
        self.rotation = r_deg
        r_rad = np.deg2rad(r_deg)
        self.model_matrix = np.array([[np.cos(r_rad), -np.sin(r_rad), 0.0, 0.0],
                                      [np.sin(r_rad), np.cos(r_rad),  0.0, 0.0],
                                      [0.0,           0.0,            1.0, 0.0],
                                      [0.0,           0.0,            0.0, 1.0]], dtype=np.float32)

    @property
    def limits(self):
        return np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    def calculate_align_offset(self):
        ofst_xy = np.array([0.0, 0.0], dtype=np.float32)

        if self.text is None or not self.glyph_offsets:
            return ofst_xy

        if self.vert_align == VerticalAlign.Baseline and self.horz_align == HorizontalAlign.Left:
            return ofst_xy

        # first get limits of text
        lm = self.get_text_range()

        if self.horz_align == HorizontalAlign.Centre:
            ofst_xy[0] = -(lm[1] + lm[3]) / 2
        elif self.horz_align == HorizontalAlign.Right:
            ofst_xy[0] = -lm[3]

        if self.vert_align == VerticalAlign.Middle:
            ofst_xy[1] = -(lm[0] - lm[2]) / 2
        elif self.vert_align == VerticalAlign.Top:
            ofst_xy[1] = -lm[0]
        elif self.vert_align == VerticalAlign.Bottom:
            ofst_xy[1] = -lm[2]

        return ofst_xy

    def get_text_range(self):
        top = 0.0
        bottom = 0.0
        left = 0.0
        right = 0.0

        for ch in self.text:
            of = self.glyph_offsets[ch]

            top = max(of[0], top)
            bottom = min(of[2], bottom)
            right += of[3]

        return np.array([top, left, bottom, right])

    def initialise(self):
        super(OglNumberTextTechnique, self).initialise()

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

    def make_buffers(self, origin, text, fontsize=10):
        flag_update_text = True
        if fontsize == self.fontsize and self.glyph_buffers:
            flag_update_text = False
        self.text = text # note that this is just kept for later, it is not used to generate anything now
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
        self.align_offset = self.calculate_align_offset()

    def _make_text_buffers(self):
        fnt = ImageFont.truetype("arial.ttf", self.fontsize)
        ascent, descent = fnt.getmetrics()

        for ch in self.glyph_text:
            # https://stackoverflow.com/questions/43060479/how-to-get-the-font-pixel-height-using-pil-imagefont

            msk = fnt.getmask(ch, mode='1')
            off_x, off_y = fnt.getoffset(ch)
            off_x_end = off_x + msk.size[0]

            text_bitmap = np.asarray(msk).reshape(msk.size[1], msk.size[0])
            text_bitmap = text_bitmap / text_bitmap.max()

            asc = ascent - off_y - 1
            dsc = text_bitmap.shape[0] - asc

            self.glyph_offsets[ch] = np.array([asc, off_x, -dsc, off_x_end], dtype=np.float32)

            self.glyph_buffers[ch] = OglTextureBuffer(text_bitmap.astype(np.float32))

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

        if not self.glyph_buffers or self.position_buffer is None:
            return

        self.enable()

        self.set_projection(projection)
        gl.glUniformMatrix4fv(self.model_location, 1, gl.GL_TRUE, self.model_matrix)
        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform1f(self.width_location, width)
        gl.glUniform1f(self.height_location, height)
        gl.glUniform1i(self.texture_unit_location, 0)
        self.position_buffer.bind()

        # only x offsets are important (to move along the baseline)
        char_offset = 0.0

        for ch in self.text:
            offset = np.copy(self.glyph_offsets[ch])
            char_offset_start = offset[3]
            offset[0] += self.align_offset[1]
            offset[1] += char_offset + self.align_offset[0]
            offset[2] += self.align_offset[1]
            offset[3] += char_offset + self.align_offset[0]
            char_offset += char_offset_start

            gl.glUniform4fv(self.offsets_location, 1, offset)

            self.glyph_buffers[ch].bind()
            gl.glDrawArrays(gl.GL_POINTS, 0, self.position_buffer.size)
            self.glyph_buffers[ch].unbind()

        self.position_buffer.unbind()
        self.disable()
