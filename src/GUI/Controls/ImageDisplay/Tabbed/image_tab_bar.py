from PyQt5 import QtWidgets, QtCore, QtGui

#
# Almost all of the code for the tab widgets is from: https://stackoverflow.com/a/63005993/13636826
#


#
#  The TabBar class re-implements some of the functionality of the QTabBar widget
class ImageTabBar(QtWidgets.QTabBar):
    onDetachTabSignal = QtCore.pyqtSignal(int, QtCore.QPoint)
    onMoveTabSignal = QtCore.pyqtSignal(int, int)
    detachedTabDropSignal = QtCore.pyqtSignal(str, int, QtCore.QPoint)

    def __init__(self, parent: QtWidgets.QTabWidget = None):
        super(ImageTabBar, self).__init__(parent)

        # self.setAcceptDrops(True)
        self.setElideMode(QtCore.Qt.ElideRight)
        self.setSelectionBehaviorOnRemove(QtWidgets.QTabBar.SelectLeftTab)

        self.dragStartPos = QtCore.QPoint()
        self.dragDropedPos = QtCore.QPoint()
        self.mouseCursor = QtGui.QCursor()
        self.dragInitiated = False
        self.processing_detach = False

    def setMovable(self, movable: bool) -> None:
        pass

    def setExpanding(self, enabled: bool) -> None:
        pass

    def tabSizeHint(self, index: int) -> QtCore.QSize:
        size = QtWidgets.QTabBar.tabSizeHint(self, index)
        w = int(self.width() / self.count())
        return QtCore.QSize(w, size.height())

    #  Send the onDetachTabSignal when a tab is double clicked
    def mouseDoubleClickEvent(self, event):
        event.accept()
        self.onDetachTabSignal.emit(self.tabAt(event.pos()), self.mouseCursor.pos())

    #  Set the starting position for a drag event when the mouse button is pressed
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragStartPos = event.pos()

        # if self.parent().widget(self.currentIndex()).objectName() == "duff_widget":
        #     self.dragStartPos = QtCore.QPoint()
        # else:
        self.dragDropedPos.setX(0)
        self.dragDropedPos.setY(0)

        self.dragInitiated = False
        self.processing_detach = False

        super(ImageTabBar, self).mousePressEvent(event)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.d_tab = None
        super(ImageTabBar, self).mouseReleaseEvent(a0)

    #  Determine if the current tab is dragged out of tab bar
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # Determine if the current movement is detected as a drag
        if not self.dragStartPos.isNull() and (
                (event.pos() - self.dragStartPos).manhattanLength() < QtWidgets.QApplication.startDragDistance()):
            self.dragInitiated = True

        if self.processing_detach:
            event.ignore()
            return

        # If the current movement is a drag initiated by the left button
        if (((event.buttons() == QtCore.Qt.LeftButton)) and self.dragInitiated):

            # This lets the default behaviour work if we are are just reordering tabs
            if self.rect().contains(event.pos()):
                # QtWidgets.QTabBar.mouseMoveEvent(self, event)
                super(ImageTabBar, self).mouseMoveEvent(event)
                return

            self.processing_detach = True
            self.parent().detachTab(self.currentIndex(), self.mouseCursor.pos())

        else:
            QtWidgets.QTabBar.mouseMoveEvent(self, event)

    # def event(self, event):
    #     if self.d_tab is not None:
    #         return self.d_tab.event(event)
    #
    # def nativeEvent(self, eventType, message):
    #     if self.d_tab is not None:
    #         return self.d_tab.nativeEvent(eventType, message)


    # ##
    # #  Determine if the drag has entered a tab position from another tab position
    # #
    # #  @param    event    a drag enter event
    # def dragEnterEvent(self, event):
    #     mimeData = event.mimeData()
    #     formats = mimeData.formats()
    #
    #     if 'action' in formats and mimeData.data('action') == 'application/tab-detach':
    #         event.acceptProposedAction()
    #
    #     QtWidgets.QTabBar.dragMoveEvent(self, event)
    #
    # ##
    # #  Get the position of the end of the drag
    # #
    # #  @param    event    a drop event
    # def dropEvent(self, event):
    #     self.dragDropedPos = event.pos()
    #     QtWidgets.QTabBar.dropEvent(self, event)
    #
    # ##
    # #  Determine if the detached tab drop event occurred on an existing tab,
    # #  then send the event to the DetachableTabWidget
    # def detachedTabDrop(self, name, dropPos):
    #
    #     tabDropPos = self.mapFromGlobal(dropPos)
    #
    #     index = self.tabAt(tabDropPos)
    #
    #     self.detachedTabDropSignal.emit(name, index, dropPos)