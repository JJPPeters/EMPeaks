from PyQt5 import QtCore, QtGui, QtWidgets

# More or less just a class the same a QTreeWidget but I filter out the mouseReleaseEvents by right click only
class ItemListWidget(QtWidgets.QTreeWidget):

    itemRightClicked = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kargs):
        super(ItemListWidget, self).__init__(*args, **kargs)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setColumnCount(4)
        self.setHeaderLabels(['',  'Name', 'Type', ''])
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.setIndentation(0)

    def mouseReleaseEvent(self, event):
        if not event.button() & QtCore.Qt.RightButton:
            super(ItemListWidget, self).mouseReleaseEvent(event)
            return

        items = self.selectedItems()
        # item = self.itemAt(event.pos())
        if not items:  # check if the list is empty
            return

        self.itemRightClicked.emit(items)

