from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
from scipy import interpolate

class GradientItem(QtWidgets.QGraphicsView):

    sigDoubleClick = QtCore.pyqtSignal()
    sigGradientChanged = QtCore.pyqtSignal(object)

    def __init__(self, orientation='horizontal', **kargs):
        super(GradientItem, self).__init__()
        self.orientation = orientation
        self.length = 100
        self.maxDim = 10
        self.rectSize = 10
        self.B = 0.5
        self.C = 1.0
        self.G = 1.0
        self.Angle = 0

        defaultColmap = [[0.0, [0, 0, 0, 255]], [1.0, [255, 255, 255, 255]]]
        self.setupColmap(defaultColmap)

        self.orientations = {'horizontal': (0, 1, 1), 'vertical': (90, 1, 1)}

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        # self.gradRect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, self.rectSize, 100, self.rectSize))
        # self.backgroundRect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, -self.rectSize, 100, self.rectSize))
        # self.backgroundRect.setBrush(QtGui.QBrush(QtCore.Qt.DiagCrossPattern))
        #
        self.setOrientation(orientation)

        # self.backgroundRect.setParentItem(self)
        # self.gradRect.setParentItem(self)

        self.setMaxDim(self.rectSize)

        self.updateGradient()

    def paint(self, p, opt, widget):
        return

    def mouseDoubleClickEvent(self, ev):
        self.sigDoubleClick.emit()

    def keyPressEvent(self, ev):
        ev.ignore()

    def setMaxDim(self, mx=None):
        if mx is None:
            mx = self.maxDim
        else:
            self.maxDim = mx

        if self.orientation == 'horizontal':
            self.setFixedHeight(mx)
            self.setMaximumWidth(16777215)
        else:
            self.setFixedWidth(mx)
            self.setMaximumHeight(16777215)

    def setFixedHeight(self, h):
        self.setMaximumHeight(h)
        self.setMinimumHeight(h)

    def setFixedWidth(self, h):
        self.setMaximumWidth(h)
        self.setMinimumWidth(h)

    def height(self):
        return self.geometry().height()

    def width(self):
        return self.geometry().width()

    def setOrientation(self, orientation):
        self.orientation = orientation
        self.setMaxDim()
        self.resetTransform()
        ort = orientation
        if ort == 'horizontal':
            self.translate(0, self.height()-1)
        elif ort == 'vertical':
            self.rotate(270)
            self.scale(1, -1)
            self.translate(-self.height()-1, 0)
        else:
            raise Exception("%s is not a valid orientation. Options are \
                            'horizontal', and 'vertical'" % str(ort))

    def widgetLength(self):
        if self.orientation == 'horizontal':
            return self.width()
        else:
            return self.height()

    def resizeEvent(self, ev):
        wlen = max(40, self.widgetLength())
        self.setLength(wlen-2)
        self.setOrientation(self.orientation)

    def setLength(self, newLen):
        self.length = float(newLen)
        # self.backgroundRect.setRect(1, -self.rectSize, newLen, self.rectSize)
        # self.gradRect.setRect(1, -self.rectSize, newLen, self.rectSize)
        self.updateGradient()

    def mouseClickEvent(self, ev):
        # add double click event to reset?
        pass

    def updateGradient(self):
        self.gradient = self.getGradient()
        # self.gradRect.setBrush(QtGui.QBrush(self.gradient))
        self.scene.setBackgroundBrush(QtGui.QBrush(self.gradient))
        self.scene.setSceneRect(QtCore.QRectF(0.0, 0, self.length, self.length))
        # self.setBackgroundBrush(QtGui.QBrush(self.gradient))
        self.sigGradientChanged.emit(self)

    def getGradient(self):
        """Return a QLinearGradient object."""
        g = QtGui.QLinearGradient(QtCore.QPointF(0, 0),
                                  QtCore.QPointF(self.length, 0))
        stops = self.stops
        g.setStops([(x, QtGui.QColor(t[0], t[1], t[2])) for x, t in stops])
        return g

    def changeColmap(self, cmap):
        self.setupColmap(cmap)
        self.doBCG()

    def setupColmap(self, cmap):
        self.origStops = []
        self.stops = []

        p = []
        r = []
        g = []
        b = []
        a = []

        if type(cmap) == np.ndarray and cmap.shape == (256, 4):
            for i in range(256):
                p.append(i / 255.0)
                r.append(cmap[i, 0])
                g.append(cmap[i, 1])
                b.append(cmap[i, 2])
                a.append(cmap[i, 3])
        else:
            for x, t in cmap:
                p.append(x)
                r.append(t[0])
                g.append(t[1])
                b.append(t[2])
                a.append(t[3])

        self.r_interp = interpolate.interp1d(p, r)
        self.g_interp = interpolate.interp1d(p, g)
        self.b_interp = interpolate.interp1d(p, b)
        self.a_interp = interpolate.interp1d(p, a)

        p = np.linspace(0.0, 1.0, 256)

        r = self.r_interp(p)
        g = self.g_interp(p)
        b = self.b_interp(p)
        a = self.a_interp(p)

        for i, j, k, l, m in zip(p, r, g, b, a):
            self.origStops.append([i, [j, k, l, m]])

        self.stops = self.origStops.copy()

    def updateBCG(self, B, C, G):
        self.B = B
        self.C = C
        self.G = G
        self.doBCG()

    def doBCG(self):
        grid = []
        p = []
        r = []
        g = []
        b = []
        a = []

        for x, t in self.origStops:
            xt = x**self.G
            xn = self.C*(xt-self.B)+0.5
            grid.append(xn)

        grid = np.clip(grid, 0.0, 1.0)

        p = np.linspace(0.0, 1.0, 256)

        r = self.r_interp(grid)
        g = self.g_interp(grid)
        b = self.b_interp(grid)
        a = self.a_interp(grid)

        self.stops = [[i, [j, k, l, m]] for i, j, k, l, m in zip(p, r, g, b, a)]

        self.updateGradient()

    def updateAngle(self, Angle):
        self.Angle = Angle
        self.doAngle()

    def doAngle(self):
        c = [i[1] for i in self.origStops]
        i = round((self.Angle / 360) * 255)
        cols = c[i:] + c[:i]

        p = np.linspace(0.0, 1.0, 256)

        self.stops = [[j, k] for j, k in zip(p, cols)]

        self.updateGradient()

    def getLookupTable(self, nPts, alpha=False, original=False):
        if alpha:
            table = np.empty((nPts, 4), dtype=np.ubyte)
        else:
            table = np.empty((nPts, 3), dtype=np.ubyte)

        for i in range(nPts):
            x = float(i)/(nPts-1)
            color = self.getColor(x, toQColor=False, original=original)
            table[i] = color[:table.shape[1]]

        return table

    def getColor(self, x, toQColor=True, original=False):
        if original:
            stops = self.origStops
        else:
            stops = self.stops

        if x <= stops[0][0]:
            c = stops[0][1]
            if toQColor:
                # always copy colors before handing them out
                return QtGui.QColor(c)
            else:
                return c[0], c[1], c[2], c[3]
        if x >= stops[-1][0]:
            c = stops[-1][1]
            if toQColor:
                # always copy colors before handing them out
                return QtGui.QColor(c)
            else:
                return c[0], c[1], c[2], c[3]

        x2 = stops[0][0]
        for i in range(1, len(stops)):
            x1 = x2
            x2 = stops[i][0]
            if x1 <= x <= x2:
                break

        dx = x2 - x1
        if dx == 0:
            f = 0.
        else:
            f = (x-x1) / dx
        c1 = stops[i-1][1]  # colour
        c2 = stops[i][1]
        # if self.colorMode == 'rgb':
        r = c1[0] * (1.-f) + c2[0] * f
        g = c1[1] * (1.-f) + c2[1] * f
        b = c1[2] * (1.-f) + c2[2] * f
        a = c1[3] * (1.-f) + c2[3] * f
        if toQColor:
            return QtGui.QColor(int(r), int(g), int(b), int(a))
        else:
            return (r, g, b, a)
