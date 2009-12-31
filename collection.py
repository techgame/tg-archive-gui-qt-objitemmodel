##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import weakref
from .apiQt import Qt, QVariant, QModelIndex, QAbstractItemModel
from .baseCollection import BaseObjectAdaptor, BaseObjectCollection

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectAdaptor(BaseObjectAdaptor):
    def __init__(self, value, parent):
        self.value = value

    def __repr__(self):
        data = self.data()
        return "<%s %r>" % (self.__class__.__name__, data)

    def flags(self, oi=None):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    def data(self, oi=None, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        return str(self.value)
    def setData(self, oi, value, role):
        return False

ObjAdaptor = ObjectAdaptor

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectCollection(BaseObjectCollection):
    _entryList = None
    def __init__(self, parent=None):
        self._ref = weakref.ref(self)
        self.init(parent)

    _parent = None
    def init(self, parent):
        if parent is not None:
            self._parent = weakref.ref(parent)

        self._entryList = []

    def _invalidate(self):
        self._childMap = None

    def parentCollection(self):
        """Returns the parent collection containing this collection.  
        
        Used to resolve parent of a model index"""
        ref = self._parent
        if ref is not None:
            return ref()
    def entryAtRowCol(self, row, column):
        """Given (row, column), returns an entry tuple of (item, collection, parent).

        Typically, only row is used to resolve down to an item."""
        return self._entryList[row]
    def rowColEntryForChild(self, child):
        """Find the (row, column) for child.  
        
        Used to resolve parent of a model index"""
        cmap = self._childRowMap()
        row = cmap.get(child, None)
        if row is None:
            return None, None, child
        entry = self._entryList[row]
        return row, 0, entry

    _childMap = None
    def _childRowMap(self):
        cmap = self._childMap
        if cmap is None:
            cmap = dict((e,r) for r,entry in enumerate(self._entryList) for e in entry)
            self._childMap = cmap
        return cmap

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def rowCount(self, oi=None):
        return len(self._entryList)

    columnNames = [""]
    def columnCount(self, oi=None):
        return len(self.columnNames)
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            try:
                return self.columnNames[section]
            except LookupError:
                return QVariant()

        return QVariant()

ObjCollection = ObjectCollection

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ ObjectCollectionEx, now with insert/append/extend api!
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectCollectionEx(ObjectCollection):
    def newEntryForData(self, data):
        """Returns a new tuple of (item, collection) for data"""
        try:
            coll = None
            if data.isObjectCollection():
                coll = data
        except AttributeError: 
            pass
        try:
            if not data.isObjectAdaptor():
                data = data.asObjectAdaptor(self)
        except AttributeError, e: 
            data = self.newAdaptorForData(data)
        return (data, coll)

    ObjectAdaptor = ObjectAdaptor
    def newAdaptorForData(self, data):
        return self.ObjectAdaptor(data, self)

    def append(self, data):
        entry = self.newEntryForData(data)
        self.appendEntry(entry)
    def appendEntry(self, entry):
        self._entryList.append(self._asEntry(entry))
        self._invalidate()

    def insert(self, index, data):
        entry = self.newEntryForData(data)
        self.insertEntry(index, entry)
    def insertEntry(self, index, entry):
        self._entryList.insert(index, self._asEntry(entry))
        self._invalidate()

    def extend(self, iterData):
        entries = (self.newEntryForData(d) for d in iterData)
        self.extendEntries(entries)
    def extendEntries(self, iterEntries):
        checkEntry = self._asEntry
        self._entryList.extend(checkEntry(e) for e in iterEntries)
        self._invalidate()

    def _asEntry(self, entry):
        """entry becomes of the form (item, collection, weakref.ref(self))"""
        if not entry[0].isObjectAdaptor():
            raise ValueError("Entry[0] is not an item adaptor")
        if entry[1] is None:
            return (entry[0], None, self._ref)

        if not entry[1].isObjectCollection():
            raise ValueError("Entry[1] is not an item collection")
        if entry[1].parentCollection() is not self:
            raise ValueError("Entry[1]'s parent does not match structure")
        return (entry[0], entry[1], self._ref)

ObjCollectionEx = ObjectCollectionEx

