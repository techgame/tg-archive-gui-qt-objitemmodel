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
from . import collectionOps as ops

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectAdaptor(BaseObjectAdaptor):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        data = self.data(None, Qt.DisplayRole)
        return "<%s %r>" % (self.__class__.__name__, data)

    _flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
    def flags(self, oi=None):
        return self._flags
    def data(self, oi=None, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        return str(self.value)
    def setData(self, oi, value, role):
        return False

    def asObjectCollection(self):
        return None

ObjAdaptor = ObjectAdaptor

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectCollection(BaseObjectCollection):
    _entryList = None

    def __init__(self, entries=None):
        self.Entry = self.Entry.newFlyweight(self)
        self.init()
        if entries:
            self.extend(entries)

    def init(self):
        self._entryList = []

    _parentCollectionRef = None
    def getParentCollection(self):
        """Returns the parent collection containing this collection.  
        
        Used to resolve parent of a model index"""
        ref = self._parentCollectionRef
        if ref is not None:
            return ref()
    def setParentCollection(self, parent):
        if parent is not None:
            parent = weakref.ref(parent)
        self._parentCollectionRef = parent

    def oiUpdate(self, oi, parentRef):
        self._parentCollectionRef = parentRef
        return self

    def entryAtRowCol(self, row, column):
        """Given (row, column), returns an entry tuple of (item, collection, parent).

        Typically, only row is used to resolve down to an item."""
        e = self._entryList[row]
        if not isinstance(e, self.Entry):
            e = self.Entry(*e)
            self._entryList[row] = e
        return e

    def rowColEntryForChild(self, child):
        """Find the (row, column) for child.  
        
        Used to resolve parent of a model index"""
        cmap = self._childRowMap()
        row = cmap.get(child, None)
        if row is None:
            return None, None, child
        entry = self.entryAtRowCol(row, 0)
        return row, 0, entry

    _childMap = None
    def _childRowMap(self):
        cmap = self._childMap
        if cmap is None:
            cmap = dict((e,r) for r,entry in enumerate(self._entryList) for e in entry)
            self._childMap = cmap
        return cmap
    def invalidateCache(self):
        self._childMap = None

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

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def normalizeEntries(self, entries):
        normItem = self.normalizeItem
        for idx,item in enumerate(entries):
            if isinstance(item, self.Entry):
                continue

            item = normItem(item)
            entries[idx] = self.Entry(*item)

    def normalizeItem(self, item):
        if isinstance(item, (tuple, list)):
            return item

        if item.isObjCollection():
            adp = item.asObjectAdaptor()
            return (adp, item)

        elif item.isObjAdaptor():
            coll = item.asObjectCollection()
            return (item, coll)

        raise ValueError("Cannot convert item into an entry")

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Change Operations
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def changeOp(self, oi=None):
        if oi is not None:
            oi = self.asObjIndex(oi)
        return ops.CollectionChangeOp(self, oi)
    def entries(self, oi=None):
        return ops.EntryListOps(self.changeOp(oi))

    def append(self, item, oi=None):
        return self.entries(oi).append(item)
    def insert(self, index, item, oi=None):
        return self.entries(oi).insert(index, item)
    def assign(self, items, oi=None):
        return self.entries(oi).assign(items)
    def extend(self, items, oi=None):
        return self.entries(oi).extend(items)
    def clear(self, items, oi=None):
        return self.entries(oi).clear(items)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ObjCollection = ObjectCollection

