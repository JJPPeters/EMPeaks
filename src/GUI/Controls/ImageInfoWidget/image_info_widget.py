from PyQt5 import QtCore, QtGui, QtWidgets
from .histogram_control_widget import HistogramControlWidget
from .direction_control_widget import DirectionControlWidget
from .item_list_widget import ItemListWidget
import numpy as np

from GUI.Utilities.enums import WindowType, AnnotationType
from Processing.Utilities.PeakFunctions.peak_functions import gaussian_2d
from GUI.Utilities import save_peaks, save_quiver

from GUI.Controls.Plot.Plottables import ImagePlot, PolarImagePlot


class ImageInfoWidget(QtWidgets.QWidget):

    sigItemDeleted = QtCore.pyqtSignal(str, bool)
    sigItemHide = QtCore.pyqtSignal(str, bool)

    def __init__(self, parent=None):
        # QtGui.QWidget.__init__(self, parent)
        super(ImageInfoWidget, self).__init__(parent)

        self.parent = parent

        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        # create colour map widgets, they both always exist, they are just hidden
        self.colMapHistogram = HistogramControlWidget(self)
        self.colMapDirection = DirectionControlWidget(self)

        # set up the list of 'objects' on the images
        self.itemsList = ItemListWidget(self)
        self.itemsList.header().setMinimumSectionSize(25)
        self.itemsList.setColumnWidth(0, 25)
        self.itemsList.setColumnWidth(1, 70)
        self.itemsList.setColumnWidth(2, 60)
        self.itemsList.setColumnWidth(3, 25)

        # add everything to our layout
        self.verticalLayout.addWidget(self.colMapHistogram)
        self.verticalLayout.addWidget(self.colMapDirection)
        self.verticalLayout.addWidget(self.itemsList)

        newSize = self.minimumSizeHint()
        self.setFixedWidth(newSize.width())

        # Due to the way that opengl works, I need to display these histogram items first
        # I hide them in the show event (as default no image is open)
        # self.colMapHistogram.hide()
        # self.colMapDirection.hide()

        self.itemsList.header().setSectionsMovable(False)

        self.itemsList.itemRightClicked.connect(self.onClickItem)
        self.itemsList.itemChanged.connect(self.toggle_visible)

    def showEvent(self, event):
        self.colMapHistogram.hide()
        self.colMapDirection.hide()

    def onClickItem(self, items):
        # if self.parent is None:
            # return
        pos = QtGui.QCursor().pos()  # get cursor position

        # make a menu to show
        menu = QtWidgets.QMenu()

        # populate it
        # noyl do export for single items at the moment
        if len(items) == 1 and items[0].text(2) == AnnotationType.Scatter.value:
            action_export = menu.addAction(self.tr("Export"))
            action_export.triggered.connect(lambda: self.peaks_export_triggered(items))
        elif len(items) == 1 and items[0].text(2) == AnnotationType.Quiver.value:
            action_export = menu.addAction(self.tr("Export"))
            action_export.triggered.connect(lambda: self.quiver_export_triggered(items))

        action_delete = menu.addAction(self.tr("Delete"))
        action_delete.triggered.connect(lambda: self.on_actionDelete_triggered(items))

        # action_toggle_visible = menu.addAction(self.tr("Toggle visible"))
        # action_toggle_visible.triggered.connect(lambda: self.on_actionHide_triggered(items))
        menu.exec_(pos)

    def peaks_export_triggered(self, item):
        tag = item[0].text(1)
        save_peaks(self.parent, tag)

    def quiver_export_triggered(self, item):
        tag = item[0].text(1)
        save_quiver(self.parent, tag)

    def on_actionDelete_triggered(self, items):
        # column 0 is the name of the item, column 1 is the type
        for i, item in enumerate(items):
            self.sigItemDeleted.emit(item.text(1), i+1 == len(items))

    def on_actionHide_triggered(self, items):
        # column 0 is the name of the item, column 1 is the type
        # need some way of indicating that the object is hidden

        # need to get the actual item that was clicked, and use that check state to set the rest

        for i, item in enumerate(items):
            self.sigItemHide.emit(item.text(1))

    def toggle_visible(self, item, col):
        # TODO: make work for all selected items
        # make other items match that state of the item that was toggled

        if col == 3:
            self.sigItemHide.emit(item.text(1), item.checkState(3) == QtCore.Qt.Checked)

    def showImageInfo(self, image):
        if image is None:
            self.clearItemList()
        else:
            self.updateItemList(image)

        if image is not None and \
                'Image' in image.plottables.keys() is not None and image.windowType == WindowType.Image:
            self.updateImageHistogram(image)
        else:
            self.updateImageHistogram(None)

    def updateImageHistogram(self, image):
        if image is None or image.image_plot is None:
            self.colMapDirection.hide()
            self.colMapHistogram.hide()
            self.colMapDirection.setImage(None)
            self.colMapHistogram.setImage(None)
        elif isinstance(image.image_plot, ImagePlot):
            self.colMapDirection.hide()
            self.colMapDirection.setImage(None)
            self.colMapHistogram.setImage(image)
            self.changeColMap(image.image_plot.colour_map)
            self.colMapHistogram.show()
        elif isinstance(image.image_plot, PolarImagePlot):
            self.colMapHistogram.hide()
            self.colMapHistogram.setImage(None)
            self.colMapDirection.setImage(image)
            self.changeColMap(image.image_plot.colour_map)
            self.colMapDirection.show()

    def updateItemList(self, image):
        self.clearItemList()

        for key, entry in image.plottables.items():
            ico = self.makeIcon(entry)

            visible = image.is_plottable_visible(key)

            self.addEntry(key, entry.plot_type, visible, icon=ico)

    def makeIcon(self, annotation):  # https://stackoverflow.com/questions/50358535/qt-is-there-a-way-to-transform-a-graphic-item-into-a-pixmap
        # I'm aiming for icons of 16x16 at the moment

        items_to_paint = []

        if isinstance(annotation, ImagePlot):
            # make a small gaussian peal :)
            sz = 16
            params = [0.0, 0.0, 1, 2, 2.0, 0.0]
            YX = np.mgrid[0:sz, 0:sz] - (sz - 1) / 2
            im = (gaussian_2d(YX, *params) * 255).astype(np.uint8)

            qim = QtGui.QImage(im, sz, sz, QtGui.QImage.Format_Grayscale8)

            pm = QtGui.QPixmap(qim)
            return QtGui.QIcon(pm)

        elif annotation.plot_type == AnnotationType.Scatter:
            # TODO: make this the right colour?
            point = QtWidgets.QGraphicsEllipseItem(2, 2, 12, 12)
            fill_col = annotation.fill_colour * 255
            border_col = annotation.border_colour * 255

            br = QtGui.QBrush(QtGui.QColor(fill_col[0], fill_col[1], fill_col[2]))
            point.setBrush(br)

            pn = QtGui.QPen(QtGui.QColor(border_col[0], border_col[1], border_col[2]))
            pn.setWidth(1)
            point.setPen(pn)

            items_to_paint.append(point)
        elif annotation.plot_type == AnnotationType.Quiver:
            # make our own arrow as it is easier to render in a pixmap
            line = QtWidgets.QGraphicsLineItem(6, 6, 14, 14)
            pn = QtGui.QPen(QtGui.QColor(230, 10, 70))
            pn.setWidth(2)
            line.setPen(pn)
            items_to_paint.append(line)

            poly = QtGui.QPolygonF()
            poly.append(QtCore.QPointF(2, 2))
            poly.append(QtCore.QPointF(11, 5))
            poly.append(QtCore.QPointF(5, 11))
            poly.append(QtCore.QPointF(2, 2))

            head = QtWidgets.QGraphicsPolygonItem(poly)
            pn = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
            pn.setWidth(0)
            head.setPen(pn)

            br = QtGui.QBrush(QtGui.QColor(230, 10, 70))
            head.setBrush(br)

            items_to_paint.append(head)
        elif annotation.plot_type == AnnotationType.Basis:
            line_a = QtWidgets.QGraphicsLineItem(2, 2, 2, 14)
            pn = QtGui.QPen(QtGui.QColor(20, 200, 70)) # width = 2
            pn.setWidth(2)
            line_a.setPen(pn)
            items_to_paint.append(line_a)

            line_b = QtWidgets.QGraphicsLineItem(2, 14, 14, 14)
            pn = QtGui.QPen(QtGui.QColor(230, 10, 70)) # width = 2
            pn.setWidth(2)
            line_b.setPen(pn)
            items_to_paint.append(line_b)

        pm = QtGui.QPixmap(16, 16)
        pm.fill(QtGui.QColor(0, 0, 0, 0))
        pntr = QtGui.QPainter(pm)
        # painter.setRenderHint(QPainter::Antialiasing); from C++

        opt = QtWidgets.QStyleOptionGraphicsItem()
        for item in items_to_paint:
            item.paint(pntr, opt)

        pntr.end()

        return QtGui.QIcon(pm)

    def addEntry(self, tag, tag_type: AnnotationType, visible, icon=None):
        # if icon is None, just do nothing and leave the cell blank
        item = QtWidgets.QTreeWidgetItem()

        # item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable)

        if icon is not None:
            item.setIcon(0, icon)
        item.setText(1, tag)
        item.setText(2, tag_type.value)

        if visible:
            item.setCheckState(3, QtCore.Qt.Checked)
        else:
            item.setCheckState(3, QtCore.Qt.Unchecked)

        self.itemsList.addTopLevelItem(item)

    def clearItemList(self):
        self.itemsList.clear()

    def changeColMap(self, cmap):
        # until this point, the colourmap stil contains what submenu it is in, strip it off here (hence the [1])
        if cmap is None:
            return
        if type(cmap) == np.ndarray and cmap.shape == (256, 4):
            self.colMapHistogram.changeColmap(cmap)
            self.colMapDirection.changeColmap(cmap)
        else:
            self.colMapHistogram.changeColmap(cmap[1])
            self.colMapDirection.changeColmap(cmap[1])

    # def changeDirectionMap(self, cmap):
    #     # until this point, the colourmap stil contains what submenu it is in, strip it off here (hence the [1])
    #     self.colMapDirection.changeColmap(cmap[1])
    #
    # def changeHistogramMap(self, cmap):
    #     # until this point, the colourmap stil contains what submenu it is in, strip it off here (hence the [1])
    #     self.colMapDirection.changeColmap(cmap[1])
