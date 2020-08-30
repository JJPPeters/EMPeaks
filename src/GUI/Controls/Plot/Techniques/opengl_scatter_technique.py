import OpenGL.GL as gl
import numpy as np

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .shaders import scatter_shaders as shaders


class OglScatterTechnique(OglTechnique):

    def __init__(self, size_x=1, size_y=None, fill_colour=np.zeros((4,)),
                 border_width=1, border_colour=np.ones((4, )),
                 selected_fill_colour=None, selected_border_colour=None, use_screen_space=True,
                 z_value=1, visible=True):
        super(OglScatterTechnique, self).__init__()

        self.visible = visible

        self.deferred_make_buffer = False

        self.selected_buffer_location = None
        self.position_buffer_location = None

        self.fill_colour_location = None
        self.border_colour_location = None
        self.selected_fill_colour_location = None
        self.selected_border_colour_location = None
        self.border_thickness_location = None
        self.radii_location = None
        self.width_location = None
        self.height_location = None
        # self.screen_space_location = None

        self.position_buffer = None
        self.selected_buffer = None

        self.points = None

        self.z_location = None
        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        self.fill_colour = fill_colour.astype(np.float32)
        self.border_colour = border_colour.astype(np.float32)

        if selected_fill_colour is None:
            self.selected_fill_colour = self.border_colour
        else:
            self.selected_fill_colour = selected_fill_colour.astype(np.float32)

        if selected_border_colour is None:
            self.selected_border_colour = self.fill_colour
        else:
            self.selected_border_colour = selected_border_colour.astype(np.float32)

        self.border_thickness = float(border_width)
        r_x = float(size_x)  # this is the diameter
        r_y = r_x  # this is the diameter
        if size_y is not None:
            r_y = float(size_y)

        self.radii = np.array([r_x, r_y], dtype=np.float32)

        self.screen_space = use_screen_space

        self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    def initialise(self):
        if self.position_buffer_location is not None:
            return

        super(OglScatterTechnique, self).initialise()

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        geometry_shader_string = shaders.geometry_shader
        self.compile_shader(gl.GL_GEOMETRY_SHADER, geometry_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.projection_location = self.get_uniform_location("projection")

        self.z_location = self.get_uniform_location("z_value")

        self.fill_colour_location = self.get_uniform_location("fill_colour")
        self.border_colour_location = self.get_uniform_location("border_colour")
        self.border_thickness_location = self.get_uniform_location("border_width")

        self.selected_fill_colour_location = self.get_uniform_location("selected_fill_colour")
        self.selected_border_colour_location = self.get_uniform_location("selected_border_colour")

        self.radii_location = self.get_uniform_location("radii")
        self.width_location = self.get_uniform_location("width")
        self.height_location = self.get_uniform_location("height")

        # self.screen_space_location = self.get_uniform_location("use_screen_space")

        self.position_buffer_location = self.get_attribute_location("PosBuf")
        self.selected_buffer_location = self.get_attribute_location("SelBuf")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, positions_yx):
        self.limits[0] = np.max(positions_yx[:, 0])# + self.point_size / 2
        self.limits[1] = np.min(positions_yx[:, 1])# - self.point_size / 2
        self.limits[2] = np.min(positions_yx[:, 0])# - self.point_size / 2
        self.limits[3] = np.max(positions_yx[:, 1])# + self.point_size / 2

        self.points = positions_yx

        try:
            self._make_buffers()
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self):
        if self.position_buffer_location is None:
            raise Exception("Buffer positions are invalid")

        self.parent.makeCurrent()

        if self.position_buffer is not None and self.points.shape[0] == self.position_buffer.size:
            self.position_buffer.update_all(self.points.astype(np.float32))
            self.selected_buffer.update_all(np.zeros((self.points.shape[0], 1), dtype=np.int32))
        else:
            self.position_buffer = OglAttributeBuffer(self.points.astype(np.float32), self.position_buffer_location)
            self.selected_buffer = OglAttributeBuffer(np.zeros((self.points.shape[0], 1), dtype=np.int32), self.selected_buffer_location)

    def render(self, projection, width, height, ratio):
        if self.position_buffer is None or not self.visible:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform4fv(self.fill_colour_location, 1, self.fill_colour)
        gl.glUniform4fv(self.border_colour_location, 1, self.border_colour)

        gl.glUniform4fv(self.selected_fill_colour_location, 1, self.selected_fill_colour)
        gl.glUniform4fv(self.selected_border_colour_location, 1, self.selected_border_colour)



        gl.glUniform2fv(self.radii_location, 1, self.radii)

        if self.screen_space:
            gl.glUniform1f(self.width_location, width)
            gl.glUniform1f(self.height_location, height)
        else:
            gl.glUniform1f(self.width_location, width / ratio[0])
            gl.glUniform1f(self.height_location, height / ratio[1])

        screen_space_border = True

        if not self.screen_space:
            b_t = self.border_thickness / self.radii[0]
            if screen_space_border:
                b_t /= ratio[0]
        else:
            b_t = self.border_thickness / self.radii[0]

        gl.glUniform1f(self.border_thickness_location, b_t)

        # gl.glUniform1i(self.screen_space_location, self.screen_space)

        self.position_buffer.bind()
        self.selected_buffer.bind()

        gl.glDrawArrays(gl.GL_POINTS, 0, self.position_buffer.size)

        self.position_buffer.unbind()
        self.selected_buffer.unbind()

        self.disable()

    def set_visible(self, vis):
        self.visible = vis
