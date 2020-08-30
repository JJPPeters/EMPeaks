from PyQt5 import QtCore
import numpy as np

from .follow_dot_cursor import FollowDotCursor
from GUI.Controls.Plot.Techniques.opengl_line_technique import OglLineTechnique
from GUI.Controls.Plot.Techniques import OglScatterTechnique
from PyQt5.QtWidgets import QOpenGLWidget
from GUI.Utilities.enums import AnnotationType
from Processing.Utilities import LatticeBasis


class Basis(FollowDotCursor):
    signal_got_sub_basis = QtCore.pyqtSignal(object)

    def __init__(self, view, num_sub=1, basis=None, ave_cells=1):

        self.plot_type = AnnotationType.Basis

        self.ave_cells = ave_cells
        self.basis_cols = np.array([[255, 0, 0, 255],
                                    [0, 255, 0, 255],
                                    [0, 0, 255, 255]], dtype=np.float32) / 255
        self.z_value = 998
        self.i = 0
        self.j = 1
        if basis is None:
            self.basis = LatticeBasis(num_bases=num_sub)
        else:
            self.basis = basis

        super(Basis, self).__init__(view)

        # the view stuff
        
        #
        # This is the for normal basis
        #
        self.basis_scatter = []
        for i in range(3):
            s = OglScatterTechnique(size_x=15, border_width=0, fill_colour=self.basis_cols[i], z_value=self.z_value, visible=False)
            s.parent = self._parent
            s.make_buffers(self.basis.vector_coords[i].reshape((1, 2)))
            self.basis_scatter.append(s)

            # self._view.add_item(s)

        # now the lines

        lines = self.basis.vector_coords[[1, 0, 2], :]
        self.basis_lines = OglLineTechnique(thickness=5, colour=np.array([127, 40, 200, 255], dtype=np.float32) / 255,
                                            z_value=self.z_value, visible=False)
        self.basis_lines.parent = self._parent
        self.basis_lines.make_buffers(lines.reshape((3, 2)))
        # self._view.add_item(self.basis_lines)

        #
        # This is for the sub basis points
        #
        for i in range(1, self.basis.lattice_coords.shape[0]):
            s = OglScatterTechnique(size_x=12, border_width=0,
                                    fill_colour=np.array([0, 255, 255, 255], dtype=np.float32) / 255,
                                    z_value=self.z_value, visible=False)
            s.parent = self._parent
            s.make_buffers(self.basis.lattice_coords[i].reshape((1, 2)))
            self.basis_scatter.append(s)

            # self._view.add_item(s)

        self._visible = True

    @FollowDotCursor.parent.setter
    def parent(self, p: QOpenGLWidget):
        self._parent = p
        if self.cursor is not None:
            self.cursor.parent = p

        if self.basis_lines is not None:
            self.basis_lines.parent = self._parent
        for bs in self.basis_scatter:
            if bs is not None:
                bs.parent = self._parent

    def initialise(self):
        return

    @property
    def limits(self):
        my_lim = self.basis_lines.limits

        for p in self.basis_scatter:
            pl = p.limits

            my_lim[0] = max(pl[0], my_lim[0])  # top
            my_lim[1] = min(pl[1], my_lim[1])  # left
            my_lim[2] = min(pl[2], my_lim[2])  # bottom
            my_lim[3] = max(pl[3], my_lim[3])  # right

        return my_lim

    def render(self, projection, width, height, ratio):
        super(Basis, self).render(projection, width, height, ratio)
        self.basis_lines.render(projection, width, height, ratio)
        if len(self.basis_scatter) > 0:
            for s in self.basis_scatter:
                s.render(projection, width, height, ratio)

    def select_from_points(self, points):
        super().select_from_points(points)

        self._view.plot_view.signal_mouse_clicked.connect(self.on_basis_click)

    def on_basis_click(self, px, py, ratio):
        self.basis.vector_coords[self.i, 0] = self.y
        self.basis.vector_coords[self.i, 1] = self.x

        self.cursor.visible = False

        self.update_scatter(self.i, self.basis.vector_coords[self.i, :])

        if self.i == 2:
            self.stop_cursor()
            self._view.plot_view.signal_mouse_clicked.disconnect(self.on_basis_click)
            # convert to single lattice parameter values
            bc = self.basis.vector_coords
            # Here is where we correct for the averaging
            self.basis.vector_coords[1, :] = (bc[1, :] - bc[0, :]) / self.ave_cells + bc[0, :]
            self.basis.vector_coords[2, :] = (bc[2, :] - bc[0, :]) / self.ave_cells + bc[0, :]
            self.got_basis()
        else:
            self.i += 1

    def got_basis(self):
        # self.sigGotBasis.disconnect()
        if self.basis.num_bases < 2:
            self.basis.lattice_coords[0] = self.basis.vector_coords[0]
            self.signal_got_sub_basis.emit(self.basis)
            self.signal_got_sub_basis.disconnect()
        else:
            self.basis.lattice_coords[0] = self.basis.vector_coords[0]  # add in the first lattice
            self.start_cursor()
            self._view.plot_view.signal_mouse_clicked.connect(self.on_sub_click)

    def on_sub_click(self, evt):
        self.basis.lattice_coords[self.j, 0] = self.y  # self.x are positions of the followdotcursor
        self.basis.lattice_coords[self.j, 1] = self.x

        self.cursor.visible = False

        # + 2 to offset the normal basis (not 3 because the normal basis counts as a sub-basis)
        self.update_scatter(self.j + 2, self.basis.lattice_coords[self.j])

        if self.j >= self.basis.num_bases - 1:
            self.stop_cursor()
            self._view.plot_view.signal_mouse_clicked.disconnect(self.on_sub_click)

            self.signal_got_sub_basis.emit(self.basis)
            self.signal_got_sub_basis.disconnect()

        else:
            self.j += 1

        self._view.update()

    def update_scatter(self, i, coords):
        self.basis_scatter[i].position_buffer.update_all(coords)
        self.basis_scatter[i].visible = True

        if self.i == 1:
            lines = self.basis.vector_coords[[1, 0, 0], :]
            #lines[0] -= self.basis.vector_coords[1] - self.basis.vector_coords[0]
            #lines[-1] -= self.basis.vector_coords[0] - self.basis.vector_coords[1]

            self.basis_lines.position_buffer.update_all(lines)
            self.basis_lines.visible = True
        elif self.i == 2:
            lines = self.basis.vector_coords[[1, 0, 2], :]
            #lines[0] -= self.basis.vector_coords[1] - self.basis.vector_coords[0]
            #lines[-1] -= self.basis.vector_coords[2] - self.basis.vector_coords[0]
            self.basis_lines.position_buffer.update_all(lines)
            self.basis_lines.visible = True

        self._view.update()

    def set_visible(self, is_visible):
        for scatter in self.basis_scatter:
            scatter.visible = is_visible

        self.basis_lines.visible = is_visible

    def clear_basis(self):
        for scatter in self.basis_scatter:
            self._view.remove_item(scatter)

        self._view.remove_item(self.basis_lines)

        self.basis_scatter.clear()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        for scatter in self.basis_scatter:
            scatter.visible = value

        self.basis_lines.visible = value
