#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import weakref
from baseCollectionModel import Qt, QVariant, QModelIndex
from baseCollectionModel import BaseItemCollection, BaseCollectionItemModel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicItemAdaptor(object):
    def __init__(self, value, parent):
        self.value = value
    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.value)

    def isItemAdaptor(self): return True
    def isItemCollection(self): return False

    def flags(self, oi):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    def data(self, oi, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        return str(self.value)
    def setData(self, oi, value, role):
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicItemCollection(BaseItemCollection):
    def __init__(self, parent=None):
        self.init(parent)

    def isCollectableItem(self): return True
    def isItemCollection(self): return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newEntryForData(self, data):
        """Returns a new tuple of (item, collection) for data"""
        return (BasicItemAdaptor(data, self), None)

    def append(self, data):
        entry = self.newEntryForData(data)
        self.appendEntry(entry)
    def appendEntry(self, entry):
        self._checkEntry(entry)
        self._childList.append(entry)
        self._invalidate()

    def insert(self, index, data):
        entry = self.newEntryForData(data)
        self.insertEntry(index, entry)
    def insertEntry(self, index, entry):
        self._checkEntry(entry)
        self._childList.insert(index, entry)
        self._invalidate()

    def extend(self, iterData):
        entries = (self.newEntryForData(d) for d in iterData)
        self.extendEntries(entries)
    def extendEntries(self, iterEntries):
        checkEntry = self._checkEntry
        self._childList.extend(e for e in iterEntries if checkEntry(e))
        self._invalidate()

    def _checkEntry(self, entry):
        if not entry[0].isItemAdaptor():
            raise ValueError("Entry[0] is not an item adaptor")
        if entry[1] is None:
            return True

        if not entry[1].isItemCollection():
            raise ValueError("Entry[1] is not an item collection")
        if entry[1].parentCollection() is not self:
            raise ValueError("Entry[1]'s parent does not match structure")
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    _parent = None
    def init(self, parent):
        if parent is not None:
            self._parent = weakref.ref(parent)

        self._childList = [] # child -> row, col

    def _invalidate(self):
        self._childMap = None

    def parentCollection(self):
        """Returns the parent collection containing this collection.  
        
        Used to resolve parent of a model index"""
        ref = self._parent
        if ref is not None:
            return ref()
    def childEntryAtRowCol(self, row, column):
        """Given (row, column), returns a tuple of (item, collection).

        Typically, only row is used to resolve down to an item."""
        return self._childList[row]
    def childRowColumn(self, child):
        """Find the (row, column) for child.  
        
        Used to resolve parent of a model index"""
        cmap = self._childRowMap()
        return (cmap[child], 0)

    _childMap = None
    def _childRowMap(self):
        cmap = self._childMap
        if cmap is None:
            cmap = dict((e,r) for r,entry in enumerate(self._childList) for e in entry)
            self._childMap = cmap
        return cmap

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def rowCount(self, oi):
        return len(self._childList)
    def hasChildren(self, oi):
        return bool(self._childList)
    def canFetchMore(self, oi):
        return False
    def fetchMore(self, oi):
        return None

    def columnCount(self, oi):
        return 1
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        else: return str(section+1)
    def setHeaderData(self, section, orientation, value, role):
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Collection Item Model
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicCollectionItemModel(BaseCollectionItemModel):
    def __init__(self, root):
        super(BasicCollectionItemModel, self).__init__()
        if not root.isItemCollection():
            raise ValueError("Expected an root with the item collection protocol")
        self.root = root

    def rootCollection(self):
        return self.root

    #~ rows collection protocol ~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rowCount(self, mi):
        for oi, coll in self.withObjCollection(mi):
            return coll.rowCount(oi)
        else: return 0
    def hasChildren(self, mi):
        for oi, coll in self.withObjCollection(mi):
            return coll.hasChildren(oi)
        else: return False
    def canFetchMore(self, mi):
        for oi, coll in self.withObjCollection(mi):
            return coll.canFetchMore(oi)
        else: return False
    def fetchMore(self, mi):
        for oi, coll in self.withObjCollection(mi):
            coll.fetchMore(oi)

    #~ columns collection data ~~~~~~~~~~~~~~~~~~~~~~~~~
    def headerData(self, section, orientation, role):
        coll = self.rootCollection()
        return coll.headerData(section, orientation, role)
    def setHeaderData(self, section, orientation, value, role):
        coll = self.rootCollection()
        return coll.setHeaderData(section, orientation, value, role)
    def columnCount(self, mi):
        # you could use mi, but since the header data is not index based...
        oi = self.asObjIndex(mi)
        coll = self.rootCollection()
        return coll.columnCount(oi)

    #~ item data protocol ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def flags(self, mi):
        for oi in self.withObjIndex(mi):
            return oi.item().flags(oi)
        else: return 0
    def data(self, mi, role):
        if role != Qt.DisplayRole:
            return QVariant()
        for oi in self.withObjIndex(mi):
            return oi.item().data(oi, role)
        else: return QVariant()
    def setData(self, mi, value, role):
        for oi in self.withObjIndex(mi):
            return oi.item().setData(oi, value, role)
        else: return False

CollectionItemModel = BasicCollectionItemModel