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

from .apiQt import Qt, QVariant, QModelIndex, QAbstractItemModel
from .objIndex import ObjectModelIndex

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseObjectCollectionItemModel(QAbstractItemModel):
    """BaseObjectCollection implements parnet and index based on the
    abstractions set forth by ObjectModelIndex"""

    InvalidIndex = QModelIndex
    asObjIndex = ObjectModelIndex.fromIndex

    def isObjModel(self): return True
    def isObjIndex(self): return False
    def isObjAdaptor(self): return False
    def isObjCollection(self): return False

    def rootCollection(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def parent(self, mi):
        oi = self.asObjIndex(mi)
        parent = oi.parent() if oi else None
        if parent is not None:
            return parent.asModelIndex(self)
        else: return QModelIndex()

    def oiParent(self, mi):
        miParent = self.parent(mi)
        return self.asObjIndex(miParent)

    def index(self, row, col, miParent):
        oi = self.asObjIndex(miParent)
        if oi: coll = oi.collection()
        else: coll = self.rootCollection()
        return coll.modelIndex(self, row, col)

    def oiIndex(self, row, col, miParent):
        mi = self.index(row, col, miParent)
        return self.asObjIndex(mi)

    def withObjIndex(self, mi):
        oi = self.asObjIndex(mi)
        if oi: yield oi
    def withObjCollection(self, mi, useRoot=True):
        for oi in self.withObjIndex(mi):
            coll = oi.collection()
            if coll is not None:
                yield oi, oi.collection()
            return
        if useRoot:
            yield QModelIndex(), self.rootCollection()

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
        for oi in self.withObjIndex(mi):
            return oi.item().data(oi, role)
        else: return QVariant()
    def setData(self, mi, value, role):
        for oi in self.withObjIndex(mi):
            return oi.item().setData(oi, value, role)
        else: return False

BaseObjItemModel = BaseObjectCollectionItemModel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectCollectionItemModel(BaseObjectCollectionItemModel):
    def __init__(self, root):
        super(ObjectCollectionItemModel, self).__init__()
        self.setRootCollection(root)

    _root = None
    def rootCollection(self):
        return self._root
    def setRootCollection(self, root):
        if not root.isObjCollection():
            raise ValueError("Expected an root with the item collection protocol")
        self._root = root
    root = property(rootCollection, setRootCollection)

ObjItemModel = ObjectCollectionItemModel

