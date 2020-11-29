import OpenGL.GL as gl

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .opengl_texture_buffer import OglTextureBuffer
from .shaders import image_shaders as shaders

import numpy as np

class OglImageTileTechnique(OglTechnique):

    def __init__(self,
                 pixel_scale=1.0,
                 origin=np.array([0.0, 0.0], dtype=np.float32),
                 z_value=1, visible=True):
        super(OglImageTileTechnique, self).__init__()

        self.deferred_make_buffer = False
        self.deferred_image = None

        self.coord_buffer_location = None
        self.rectangle_buffer_location = None

        self.image_buffer = None
        self.coord_buffer = None
        self.rectangle_buffer = None

        self.min_location = None
        self.max_location = None

        self.b_location = None
        self.c_location = None
        self.g_location = None

        self.colourmap_location = None
        self.texture_unit_location = None

        self.z_location = None
        self.scale_location = None
        self.origin_location = None

        self.min = 0.0
        self.max = 1.0

        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        self.visible = visible

        self.image_size = np.array([0.0, 0.0], dtype=np.float32)
        self.pixel_scale = float(pixel_scale)
        self.origin = origin.astype(np.float32)

        self.colour_map = np.zeros((256, 4), dtype=np.float32)
        self.colour_map[:, 0] = np.linspace(0, 1, 256)
        self.colour_map[:, 1] = np.linspace(0, 1, 256)
        self.colour_map[:, 2] = np.linspace(0, 1, 256)
        self.colour_map[:, 3] = 1

        self.bcg = np.array([0.5, 1.0, 1.0])

    @property
    def limits(self):
        limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        limits[0] = (self.image_size[0] * self.pixel_scale) - self.origin[0]
        limits[1] = 0 - self.origin[1]
        limits[2] = 0 - self.origin[0]
        limits[3] = (self.image_size[1] * self.pixel_scale) - self.origin[1]

        return limits

    def initialise(self):
        if self.texture_unit_location is not None:
            return

        try:
            super(OglImageTileTechnique, self).initialise()
        except Exception:
            return

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.projection_location = self.get_uniform_location("projection")

        self.z_location = self.get_uniform_location("z_value")
        self.origin_location = self.get_uniform_location("origin")
        self.scale_location = self.get_uniform_location("scale")

        self.min_location = self.get_uniform_location("image_min")
        self.max_location = self.get_uniform_location("image_max")

        self.b_location = self.get_uniform_location("brightness")
        self.c_location = self.get_uniform_location("contrast")
        self.g_location = self.get_uniform_location("gamma")

        self.colourmap_location = self.get_uniform_location("colour_map")

        self.texture_unit_location = self.get_uniform_location("tex_unit")

        self.rectangle_buffer_location = self.get_attribute_location("rectangle_position")
        self.coord_buffer_location = self.get_attribute_location("tex_coords")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, image, h_o=0, v_o=0, pixel_scale=1.0, correction=0.5, image_min=None, image_max=None):
        # first we need to get a buffer of intensities
        if image_min is None:
            self.min = np.min(image)
        else:
            self.min = image_min

        if image_max is None:
            self.max = np.max(image) - self.min
        else:
            self.max = image_max

        self.image_size[0] = image.shape[0]
        self.image_size[1] = image.shape[1]
        self.pixel_scale = float(pixel_scale)
        self.origin = np.array([v_o, h_o], dtype=np.float32)

        self.deferred_image = image

        try:
            self._make_buffers()
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self):
        self.parent.makeCurrent()

        t = self.limits[0]
        l = self.limits[1]
        b = self.limits[2]
        r = self.limits[3]

        positions = np.array([[l, b],
                              [r, b],
                              [r, t],
                              [r, t],
                              [l, t],
                              [l, b]], dtype=np.float32)

        coords = np.array([[0, 0],
                           [1, 0],
                           [1, 1],
                           [1, 1],
                           [0, 1],
                           [0, 0]], dtype=np.float32)

        if self.rectangle_buffer_location is None or self.coord_buffer_location is None:
            raise Exception("Buffer positions are invalid")

        self.image_buffer = OglTextureBuffer(self.deferred_image.astype(np.float32))
        self.coord_buffer = OglAttributeBuffer(coords, self.coord_buffer_location)
        self.rectangle_buffer = OglAttributeBuffer(positions, self.rectangle_buffer_location)

        self.deferred_image = None
        self.deferred_make_buffer = False

    def render(self, projection, width, height, ratio, clockwise=False):
        if not self.visible:
            return

        if self.image_buffer is None or self.rectangle_buffer is None or self.coord_buffer is None:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform1f(self.scale_location, self.pixel_scale)
        gl.glUniform2fv(self.origin_location, 1, self.origin)

        gl.glUniform1f(self.min_location, self.min)
        gl.glUniform1f(self.max_location, self.max)

        b = self.bcg[0]
        c = self.bcg[1]
        g = self.bcg[2]

        gl.glUniform1f(self.b_location, b)
        gl.glUniform1f(self.c_location, c)
        gl.glUniform1f(self.g_location, g)

        gl.glUniform1i(self.texture_unit_location, 0)

        gl.glUniform4fv(self.colourmap_location, 256, self.colour_map)

        self.image_buffer.bind()
        self.rectangle_buffer.bind()
        self.coord_buffer.bind()

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.rectangle_buffer.size)

        self.image_buffer.unbind()
        self.rectangle_buffer.unbind()
        self.coord_buffer.unbind()

        self.disable()
