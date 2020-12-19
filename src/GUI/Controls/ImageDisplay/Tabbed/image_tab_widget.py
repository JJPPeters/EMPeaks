from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from typing import Optional

import win32api
import win32con
import win32gui
from ctypes import windll

from GUI.Controls.ImageDisplay.Tabbed import ImageTabBar

#
# Almost all of the code for the tab widgets is from: https://stackoverflow.com/a/50693795/13636826
#

class ImageTabWidget(QtWidgets.QTabWidget):
    def __init__(self, main_window, parent=None):
        super(ImageTabWidget, self).__init__(parent)

        self.tabBar = ImageTabBar(self)
        self.tabBar.onDetachTabSignal.connect(self.detachTab)
        # self.tabBar.onMoveTabSignal.connect(self.moveTab)
        # self.tabBar.detachedTabDropSignal.connect(self.detachedTabDrop)

        self.setTabBar(self.tabBar)

        self.tabBar.setVisible(True)

        # Used to keep a reference to detached tabs since their QMainWindow
        # does not have a parent
        self.detachedTabs = {}

        # Close all detached tabs if the application is closed explicitly
        # QtWidgets.qApp.aboutToQuit.connect(self.closeDetachedTabs)  # @UndefinedVariable

        #
        # My stuff
        #
        # super(ImageTabBar, self.tabBar).setExpanding(True)
        self.set_as_dummy_only(True)

        self.main_window = main_window
        self.currentChanged.connect(self.set_tab_as_active)
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBar.setExpanding(True)

        sp = self.tabBar.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.tabBar.setSizePolicy(sp)

        self.duff_widget = QtWidgets.QWidget(self)
        self.duff_widget.setObjectName("duff_widget")
        self.addTab(self.duff_widget, " ")

    ##
    #  The default functionality of QTabWidget must remain disabled
    #  so as not to conflict with the added features
    def setMovable(self, movable):
        pass

    def setTabsClosable(self, closable):
        pass

    def set_as_dummy_only(self, dummy_only: bool):
        super(ImageTabWidget, self).setTabsClosable(not dummy_only)
        super(ImageTabBar, self.tabBar).setMovable(not dummy_only)

    def addTab(self, widget: QtWidgets.QWidget, a1: str) -> Optional[int]:
        if self.count() != 0 and widget.objectName() == "duff_widget":
            return None

        if self.count() == 1 and self.widget(0).objectName() == "duff_widget":
            self.removeTab(0)
            self.set_as_dummy_only(False)

        return super(ImageTabWidget, self).addTab(widget, a1)

    def set_tab_as_active(self, index):
        if index == -1:
            tid = None
        else:
            try:
                tid = self.widget(index).id
            except AttributeError:
                return

        self.main_window.last_active = tid

    def close_tab(self, index):
        try:
            tid = self.widget(index).id
        except AttributeError:
            return
        self.main_window.remove_image(tid)
        self.removeTab(index)

    def resizeEvent(self, event):
        self.tabBar.setFixedWidth(self.width())
        # TODO: do this programmatically somehow
        # self.tabBar.setFixedHeight(24)
        super(ImageTabWidget, self).resizeEvent(event)

    ##
    #  Move a tab from one position (index) to another
    #
    #  @param    fromIndex    the original index location of the tab
    #  @param    toIndex      the new index location of the tab
    # @pyqtSlot(int, int)
    # def moveTab(self, fromIndex, toIndex):
        # widget = self.widget(fromIndex)
        # icon = self.tabIcon(fromIndex)
        # text = self.tabText(fromIndex)
        #
        # self.removeTab(fromIndex)
        # self.insertTab(toIndex, widget, icon, text)
        # self.setCurrentIndex(toIndex)
        # return

    ##
    #  Detach the tab by removing it's contents and placing them in
    #  a DetachedTab window
    #
    #  @param    index    the index location of the tab to be detached
    #  @param    point    the screen position for creating the new DetachedTab window
    @pyqtSlot(int, QtCore.QPoint)
    def detachTab(self, index, point: QtCore.QPoint):

        # Get the tab content
        name = self.tabText(index)
        icon = self.tabIcon(index)
        if icon.isNull():
            icon = self.window().windowIcon()
        contentWidget = self.widget(index)

        try:
            contentWidgetRect = contentWidget.frameGeometry()
        except AttributeError:
            return

        # Create a new detached tab window
        detachedTab = DetachedTab(name, contentWidget)
        detachedTab.setWindowModality(QtCore.Qt.NonModal)
        detachedTab.setWindowIcon(icon)
        detachedTab.setGeometry(contentWidgetRect)

        if self.count() == 0:
            self.set_as_dummy_only(True)
            self.addTab(self.duff_widget, " ")

        # point = QtGui.QCursor.pos()
        # tbar_height = detachedTab.style().pixelMetric(QtWidgets.QStyle.PM_TitleBarHeight)
        # tbar_width = detachedTab.width()
        # detachedTab.move(point.x() - int(tbar_width / 2), point.y() - int(tbar_height / 2))

        detachedTab.show()
        # QtWidgets.QApplication.processEvents()

        # https://stackoverflow.com/questions/3720968/win32-simulate-a-click-without-simulating-mouse-movement



        x, y = win32api.GetCursorPos()
        win32api.ClipCursor((x - 1, y - 1, x + 1, y + 1))
        point = QtGui.QCursor.pos()

        # # put the middle of the title bar under the mouse
        tbar_height = detachedTab.style().pixelMetric(QtWidgets.QStyle.PM_TitleBarHeight)
        tbar_width = detachedTab.width()
        detachedTab.move(point.x() - int(tbar_width / 2), point.y() - int(tbar_height / 2))
        QtWidgets.QApplication.processEvents()

        if QtWidgets.QApplication.mouseButtons() == QtCore.Qt.LeftButton:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_ABSOLUTE, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_ABSOLUTE, 0, 0)
        win32api.ClipCursor((0, 0, 0, 0))

    # ##
    # #  Re-attach the tab by removing the content from the DetachedTab window,
    # #  closing it, and placing the content back into the DetachableTabWidget
    # #
    # #  @param    contentWidget    the content widget from the DetachedTab window
    # #  @param    name             the name of the detached tab
    # #  @param    icon             the window icon for the detached tab
    # #  @param    insertAt         insert the re-attached tab at the given index
    # def attachTab(self, contentWidget, name, icon, insertAt=None):
    #
    #     # Make the content widget a child of this widget
    #     contentWidget.setParent(self)
    #
    #     # Remove the reference
    #     del self.detachedTabs[name]
    #
    #     # Create an image from the given icon (for comparison)
    #     if not icon.isNull():
    #         try:
    #             tabIconPixmap = icon.pixmap(icon.availableSizes()[0])
    #             tabIconImage = tabIconPixmap.toImage()
    #         except IndexError:
    #             tabIconImage = None
    #     else:
    #         tabIconImage = None
    #
    #     # Create an image of the main window icon (for comparison)
    #     if not icon.isNull():
    #         try:
    #             windowIconPixmap = self.window().windowIcon().pixmap(icon.availableSizes()[0])
    #             windowIconImage = windowIconPixmap.toImage()
    #         except IndexError:
    #             windowIconImage = None
    #     else:
    #         windowIconImage = None
    #
    #     # Determine if the given image and the main window icon are the same.
    #     # If they are, then do not add the icon to the tab
    #     if tabIconImage == windowIconImage:
    #         if insertAt == None:
    #             index = self.addTab(contentWidget, name)
    #         else:
    #             index = self.insertTab(insertAt, contentWidget, name)
    #     else:
    #         if insertAt == None:
    #             index = self.addTab(contentWidget, icon, name)
    #         else:
    #             index = self.insertTab(insertAt, contentWidget, icon, name)
    #
    #     # Make this tab the current tab
    #     if index > -1:
    #         self.setCurrentIndex(index)
    #
    # ##
    # #  Remove the tab with the given name, even if it is detached
    # #
    # #  @param    name    the name of the tab to be removed
    # def removeTabByName(self, name):
    #
    #     # Remove the tab if it is attached
    #     attached = False
    #     for index in range(self.count()):
    #         if str(name) == str(self.tabText(index)):
    #             self.removeTab(index)
    #             attached = True
    #             break
    #
    #     # If the tab is not attached, close it's window and
    #     # remove the reference to it
    #     if not attached:
    #         for key in self.detachedTabs:
    #             if str(name) == str(key):
    #                 self.detachedTabs[key].onCloseSignal.disconnect()
    #                 self.detachedTabs[key].close()
    #                 del self.detachedTabs[key]
    #                 break
    #
    # ##
    # #  Handle dropping of a detached tab inside the DetachableTabWidget
    # #
    # #  @param    name     the name of the detached tab
    # #  @param    index    the index of an existing tab (if the tab bar
    # #                     determined that the drop occurred on an
    # #                     existing tab)
    # #  @param    dropPos  the mouse cursor position when the drop occurred
    # @QtCore.pyqtSlot(str, int, QtCore.QPoint)
    # def detachedTabDrop(self, name, index, dropPos):
    #
    #     # If the drop occurred on an existing tab, insert the detached
    #     # tab at the existing tab's location
    #     if index > -1:
    #
    #         # Create references to the detached tab's content and icon
    #         contentWidget = self.detachedTabs[name].contentWidget
    #         icon = self.detachedTabs[name].windowIcon()
    #
    #         # Disconnect the detached tab's onCloseSignal so that it
    #         # does not try to re-attach automatically
    #         self.detachedTabs[name].onCloseSignal.disconnect()
    #
    #         # Close the detached
    #         self.detachedTabs[name].close()
    #
    #         # Re-attach the tab at the given index
    #         self.attachTab(contentWidget, name, icon, index)
    #
    #
    #     # If the drop did not occur on an existing tab, determine if the drop
    #     # occurred in the tab bar area (the area to the side of the QTabBar)
    #     else:
    #
    #         # Find the drop position relative to the DetachableTabWidget
    #         tabDropPos = self.mapFromGlobal(dropPos)
    #
    #         # If the drop position is inside the DetachableTabWidget...
    #         if tabDropPos in self.rect():
    #
    #             # If the drop position is inside the tab bar area (the
    #             # area to the side of the QTabBar) or there are not tabs
    #             # currently attached...
    #             if tabDropPos.y() < self.tabBar.height() or self.count() == 0:
    #                 # Close the detached tab and allow it to re-attach
    #                 # automatically
    #                 self.detachedTabs[name].close()
    #
    # ##
    # #  Close all tabs that are currently detached.
    # def closeDetachedTabs(self):
    #     listOfDetachedTabs = []
    #
    #     for key in self.detachedTabs:
    #         listOfDetachedTabs.append(self.detachedTabs[key])
    #
    #     for detachedTab in listOfDetachedTabs:
    #         detachedTab.close()







##
#  When a tab is detached, the contents are placed into this QMainWindow.  The tab
#  can be re-attached by closing the dialog or by dragging the window into the tab bar
class DetachedTab(QtWidgets.QMainWindow):
    onCloseSignal = pyqtSignal(QtWidgets.QWidget, str, QtGui.QIcon)
    onDropSignal = pyqtSignal(str, QtCore.QPoint)

    def __init__(self, name, content_widget):
        QtWidgets.QMainWindow.__init__(self, None)

        # self.setObjectName(name)
        self.setWindowTitle("lol")

        self.central_tab_widget = ImageTabWidget(self)

        self.central_tab_widget.addTab(content_widget, name)

        self.setCentralWidget(self.central_tab_widget)

        # self.fake_mouse_down = True

        # self.contentWidget.show()

        # self.windowDropFilter = self.WindowDropFilter()
        # self.installEventFilter(self.windowDropFilter)
        # self.windowDropFilter.onDropSignal.connect(self.windowDropSlot)


    def event(self, event):
    #
        if event.type() == QtCore.QEvent.NonClientAreaMouseButtonRelease:
            # for getting all widgets under mouse
            # https://stackoverflow.com/a/27417852/13636826

            pos = QtGui.QCursor.pos()

            self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            widget_at = QtWidgets.qApp.widgetAt(pos)

            if type(widget_at) == ImageTabBar:
                print("I should drop!")

            self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)

        return super(DetachedTab, self).event(event)

    ##
    #  Handle a window drop event
    #
    #  @param    dropPos    the mouse cursor position of the drop
    # @QtCore.pyqtSlot(QtCore.QPoint)
    def windowDropSlot(self, dropPos):
        self.onDropSignal.emit(self.objectName(), dropPos)

    ##
    #  If the window is closed, emit the onCloseSignal and give the
    #  content widget back to the DetachableTabWidget
    #
    #  @param    event    a close event
    # def closeEvent(self, event):
    #     self.onCloseSignal.emit(self.central_tab_widget, self.objectName(), self.windowIcon())