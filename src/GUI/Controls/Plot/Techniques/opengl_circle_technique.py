import OpenGL.GL as gl

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .shaders import circle_shaders as shaders

import numpy as np

# TODO: this is very similar to the scatter plot at the moment. I think my general plan is to have this be able to have different colours/sizes etc per item, whereas scatter is consistent
class OglCircleTechnique(OglTechnique):

    def __init__(self, fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), ring_frac=0, border_width=2,
                 z_value=1, visible=True):
        super(OglCircleTechnique, self).__init__()

        self.visible = visible

        self.fill_colour_location = None
        self.border_colour_location = None
        self.border_width_x_location = None
        self.border_width_y_location = None
        self.width_location = None
        self.height_location = None

        self.ring_frac_location = None
        self.radii_location = None
        self.centre_location = None

        self.centre_buffer = None

        self.z_location = None
        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        # self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

        self.fill_colour = fill_colour.astype(np.float32)
        self.border_colour = border_colour.astype(np.float32)
        self.border_width = float(border_width)

        self.centre = np.array([0, 0], dtype=np.float32)
        self.radii = np.array([10, 10], dtype=np.float32)
        self.ring_frac = ring_frac

    @property
    def limits(self):
        t = self.centre[1] + self.radii[1]
        l = self.centre[0] - self.radii[0]
        b = self.centre[1] - self.radii[1]
        r = self.centre[0] + self.radii[0]

        return np.array([t, l, b, r], dtype=np.float32)

    def initialise(self):
        super(OglCircleTechnique, self).initialise()

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        geometry_shader_string = shaders.geometry_shader
        self.compile_shader(gl.GL_GEOMETRY_SHADER, geometry_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.projection_location = self.get_uniform_location("projection")
        self.z_location = self.get_uniform_location("z_value")
        self.centre_location = self.get_attribute_location("circle_centre")
        self.radii_location = self.get_uniform_location("circle_radii")

        self.width_location = self.get_uniform_location("width")
        self.height_location = self.get_uniform_location("height")

        self.fill_colour_location = self.get_uniform_location("fill_colour")
        self.border_colour_location = self.get_uniform_location("border_colour")
        self.border_width_x_location = self.get_uniform_location("border_width_x")
        self.border_width_y_location = self.get_uniform_location("border_width_y")
        self.ring_frac_location = self.get_uniform_location("ring_frac")

    def make_buffers(self, c_x, c_y, r_x, r_y):
        # doesnt actually set buffers!
        self.centre = np.array([c_x, c_y], dtype=np.float32)
        self.radii = np.array([r_x, r_y], dtype=np.float32)

        self.centre_buffer = OglAttributeBuffer(self.centre.reshape((1, 2)), self.centre_location)

    def render(self, projection, width, height, ratio):
        if not self.visible:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)

        b_t_x = self.border_width / self.radii[0]
        b_t_y = self.border_width / self.radii[1]
        b_t_x = b_t_x / ratio[0]
        b_t_y = b_t_y / ratio[1]

        gl.glUniform2fv(self.radii_location, 1, self.radii * 2)

        gl.glUniform4fv(self.fill_colour_location, 1, self.fill_colour)
        gl.glUniform4fv(self.border_colour_location, 1, self.border_colour)
        gl.glUniform1f(self.border_width_x_location, b_t_x / 4)
        gl.glUniform1f(self.border_width_y_location, b_t_y / 4)
        gl.glUniform1f(self.ring_frac_location, self.ring_frac)

        gl.glUniform1f(self.width_location, width / ratio[0])
        gl.glUniform1f(self.height_location, height / ratio[1])

        self.centre_buffer.bind()

        gl.glDrawArrays(gl.GL_POINTS, 0, self.centre_buffer.size)

        self.centre_buffer.unbind()

        self.disable()
