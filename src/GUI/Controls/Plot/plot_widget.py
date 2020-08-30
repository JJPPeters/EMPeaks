import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets

from .Techniques import GLPlotWidget
import OpenGL.GL as gl
from .Techniques.opengl_error import have_valid_context

from .plot_axis import Axis, AxisLocation
from .plot_view import PlotView

from GUI.Controls.Plot.Techniques.opengl_image_technique import OglImageTechnique
from GUI.Controls.Plot.Techniques.opengl_framebuffer import OglFramebuffer


class PlotWidget(GLPlotWidget):
    def __init__(self, parent=None, show_axes=False):
        super(PlotWidget, self).__init__(parent)

        #
        # Mouse interaction stuffs
        #

        self.setMouseTracking(True)
        self.clicked_object = None

        #
        #
        #

        self.background_colour = np.array([50, 0, 50, 255], dtype=np.float32) / 255

        # These aren't really needed, but I want to make this clear: The coordinate system here is 0-1
        self.x_limits = [0.0, self.width()]
        self.y_limits = [0.0, self.height()]

        self.top_border_size = 0
        self.left_border_size = 0
        self.bottom_border_size = 0
        self.right_border_size = 0

        if show_axes:
            # border sizes in pixels
            self.top_border_size = 20
            self.left_border_size = 64
            self.bottom_border_size = 64
            self.right_border_size = 20

        #
        # Axes
        #

        line_width = 3
        colour = np.array([1.0,1.0,1.0,1.0], dtype=np.float32)

        self.top_axis = None
        self.left_axis = None
        self.bottom_axis = None
        self.right_axis = None

        if show_axes:
            self.top_axis = Axis(self, AxisLocation.Top, line_width=line_width, colour=colour)
            self.left_axis = Axis(self, AxisLocation.Left, line_width=line_width, colour=colour)
            self.bottom_axis = Axis(self, AxisLocation.Bottom, line_width=line_width, colour=colour)
            self.right_axis = Axis(self, AxisLocation.Right, line_width=line_width, colour=colour)

        #
        # ViewBox
        #

        self.plot_view = PlotView(self.top_border_position, self.left_border_position, self.bottom_border_position, self.right_border_position)

        #
        # Add to plot (order is important!)
        #

        self.add_item(self.plot_view)

        if self.draw_axes:
            self.plot_view.signal_plot_range_changed.connect(self.top_axis.set_tick_positions)
            self.plot_view.signal_plot_range_changed.connect(self.bottom_axis.set_tick_positions)
            self.plot_view.signal_plot_range_changed.connect(self.left_axis.set_tick_positions)
            self.plot_view.signal_plot_range_changed.connect(self.right_axis.set_tick_positions)

            self.add_item(self.top_axis)
            self.add_item(self.bottom_axis)
            self.add_item(self.left_axis)
            self.add_item(self.right_axis)

    def setInvertY(self, inv):
        self.plot_view.view_camera.invert_y = inv

    @property
    def draw_axes(self):
        return self.top_axis is not None and self.bottom_axis is not None and self.left_axis is not None and self.right_axis is not None

    @property
    def top_border_position(self):
        return self.top_border_size

    @property
    def left_border_position(self):
        return self.left_border_size

    @property
    def bottom_border_position(self):
        return self.height() - self.bottom_border_size

    @property
    def right_border_position(self):
        return self.width() - self.right_border_size

    @property
    def x_range(self):
        return self.x_limits[1] - self.x_limits[0]

    @property
    def y_range(self):
        return self.y_limits[1] - self.y_limits[0]

    def resizeGL(self, w, h):
        self.x_limits[1] = w
        self.y_limits[1] = h

        if self.draw_axes:
            self.top_axis.update_positions()
            self.left_axis.update_positions()
            self.bottom_axis.update_positions()
            self.right_axis.update_positions()

        pr = 1#self.plot_camera.pixel_ratio
        self.plot_view.resize(pr*w, pr*h)

        return super(PlotWidget, self).resizeGL(w, h)

    def mousePressEvent(self, event):
        self.makeCurrent()

        pos_x = event.pos().x()
        pos_y = event.pos().y()

        self.clicked_object = None

        # test if an object wants to accept our click
        for item in self.techniques:
            # this part here is important, as the item itself may not be the exact widget we need to propogate drag
            # events to (i.e. this may be the handle of an annotation)
            if self.clicked_object is None:
                grabber = item.on_mouse_press(pos_x, pos_y, event.button(), event.modifiers())
                # we now have the item we clicked on, but we need to still handle the rest of the objects so they can be
                # unselected if needed
                if grabber is not None:
                    self.clicked_object = grabber
            else:
                item.selected = False

        # this is mostly to update selection graphics when clicking on/off objects
        self.update()

    def mouseMoveEvent(self, event):
        self.makeCurrent()

        pos_x = event.pos().x()
        pos_y = event.pos().y()

        # purely for displaying mouse positions
        self.plot_view.emit_mouse_coordinates(pos_x, pos_y)

        # this is where things like dragging is implemented
        if self.clicked_object is not None:
            self.clicked_object.on_mouse_move(pos_x, pos_y, event.buttons(), event.modifiers())
            self.update()

    def mouseReleaseEvent(self, event):
        self.makeCurrent()

        # these are the pixel coordinates of the event w.r.t the top left corner of this widget
        pos_x = event.pos().x()
        pos_y = event.pos().y()

        if self.clicked_object is not None:
            self.clicked_object.on_mouse_release(pos_x, pos_y, event.button(), event.modifiers())
            self.update()

        self.clicked_object = None

    def wheelEvent(self, event):
        self.makeCurrent()

        if event.angleDelta().y() != 0:

            pos_x = event.pos().x()
            pos_y = event.pos().y()

            for item in self.techniques:
                grabbed = item.on_mouse_scroll(pos_x, pos_y, event.angleDelta().y())

                if grabbed is not None:
                    break

            self.update()


    def export_display(self, scale=1, fit_view=True, image_only=False):


        # TODO: the fit view part of this is only applicable to things without axes (if I ever add this in the future)

        # TODO: I can maybe forsee a problem when trying to save this as really, really large
        # I might need to so a similar thing to the image tiling, where I render it is parts
        # maximum will be something like 8192 on most machines
        # maye I got around this by using render buffers for my framebuffers?
        if not have_valid_context():
            return

        # get values we want to reset later
        orig_view_lims = np.copy(self.plot_view.view_camera.projection_edges)
        orig_w = self.framebuffer.width
        orig_h = self.framebuffer.height

        # https://stackoverflow.com/a/42736631
        # get our context so we can copy it
        ctx = self.context()

        screen_id = QtWidgets.QApplication.desktop().screenNumber(self)
        screen = QtWidgets.QApplication.desktop().screen(screen_id)
        pr = screen.devicePixelRatio()

        # create off screen surface to render to
        surface = QtGui.QOffscreenSurface()
        surface.setFormat(ctx.format())
        surface.setScreen(ctx.screen())
        surface.create()

        # make this ocntext current with our surface
        ctx.makeCurrent(surface)

        if fit_view:
            # get limits of the view
            limits = self.plot_view.scene_limits()
            ww = (limits[3] - limits[1])
            hh = (limits[0] - limits[2])

            # set camera projection to limits of our view
            self.plot_view.view_camera.set_projection_limits(limits[0], limits[1], limits[2], limits[3])

        else:
            ww = self.width() * pr
            hh = self.height() * pr

        # these widths are for scaling
        o_w = int(ww)
        o_h = int(hh)

        # set the width of our output
        w = int(o_w * scale)
        h = int(o_h * scale)

        # resize our framebuffer for this
        # TODO: may want to just create a new one just for this export?
        self.framebuffer.resize(w, h)

        #
        # Do the rendering
        #

        # bind our framebuffer to render to
        self.framebuffer.bind()

        gl.glClearColor(*self.background_colour)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if fit_view:
            # set our viewport (not sure if scissor is needed?)
            gl.glViewport(0, 0, int(o_w * scale), int(o_h * scale))
            ratio = (scale, scale)

            # TODO: I don't think the pixel ratio thing is properly used here?

            projection = self.plot_view.view_camera.get_projection_matrix()
            if image_only:
                for technique in self.plot_view.widgets:
                    if isinstance(technique, OglImageTechnique):
                        technique.render(projection, o_w/pr, o_h/pr, ratio)
            else:
                for technique in self.plot_view.widgets:
                    technique.render(projection, o_w/pr, o_h/pr, ratio)
        else:
            gl.glViewport(0, 0, o_w, o_h)
            ratio = (scale, scale)

            projection = self.plot_camera.get_projection_matrix()

            for technique in self.techniques:
                technique.render(projection, o_w, o_h, ratio)

        self.framebuffer.unbind()

        #
        # End of render
        #

        # Copy the framebuffer to a buffer we can read from
        export_buffer = OglFramebuffer(w, h, scaling=1, multisample=1)
        self.framebuffer.blit(export_buffer.fbo)

        # reset our context (is this needed?)
        self.makeCurrent()

        # reset our camera/buffer
        self.framebuffer.resize(orig_w, orig_h)
        self.plot_view.view_camera.projection_edges = orig_view_lims

        # read and return from our new framebuffer
        return export_buffer.read_data()

