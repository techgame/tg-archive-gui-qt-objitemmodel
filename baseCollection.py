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

from .objIndex import ObjectCollectionEntry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseObjectAdaptor(object):
    def isObjAdaptor(self): return True
    def isObjCollection(self): return False
    def isObjIndex(self): return False
    def isObjModel(self): return False

    def oiUpdate(self, oi, parentRef):
        return self
    def flags(self, oi=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def data(self, oi=None, role=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def setData(self, oi, value, role):
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseObjectCollection(object):
    Entry = ObjectCollectionEntry

    def __init__(self, entries=None):
        self.Entry = self.Entry.newFlyweight(self)

    def isObjAdaptor(self): return False
    def isObjCollection(self): return True
    def isObjIndex(self): return False
    def isObjModel(self): return False

    def getParentCollection(self):
        """Returns the parent collection containing this collection.  
        
        Used to resolve parent of a model index"""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def entryAtRowCol(self, row, column):
        """Given (row, column), returns an entry tuple of (item, collection, parent).

        Typically, only row is used to resolve down to an item."""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def rowColEntryForChild(self, child):
        """Find the (row, column, entry) for item or collection child.
        
        Used to resolve parent of a model index"""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def isValidRowCol(self, row, col):
        try: 
            return self.entryAtRowCol(row, col) is not None
        except LookupError: pass
        return False

    def childEntryAt(self, oi):
        return self.entryAtRowCol(oi.row(), oi.column())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def asObjIndex(self, model):
        if model.isObjModel():
            mi = self.asModelIndex(model)
            oi = model.asObjIndex(mi)
        elif model.isObjIndex():
            oi = model
        else:
            raise ValueError("Expected a ObjectModel to resolve model index against")
        return oi
        
    def asModelIndex(self, qItemModel):
        p = self.getParentCollection()
        if p is None: 
            return qItemModel.InvalidIndex()
        return p.modelIndexForChild(qItemModel, self) 
    def modelIndexForChild(self, qItemModel, child):
        row, col, entry = self.rowColEntryForChild(child)
        if row is None: 
            return qItemModel.InvalidIndex()
        return qItemModel.createIndex(row, col, entry)
    def modelIndex(self, qItemModel, row, col=0):
        try: entry = self.entryAtRowCol(row, col)
        except LookupError:
            return qItemModel.InvalidIndex()
        return qItemModel.createIndex(row, col, entry)

    def oiUpdate(self, oi, parentRef):
        return self

    def rootCollection(self):
        coll = self
        while 1:
            parent = coll.getParentCollection()
            if parent is None:
                return coll
            else: coll = parent

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def rowCount(self, oi=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def hasChildren(self, oi=None):
        return 0<self.rowCount()

    def canFetchMore(self, oi=None):
        return False
    def fetchMore(self, oi=None):
        return None

    def columnCount(self, oi=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def headerData(self, section, orientation, role=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def setHeaderData(self, section, orientation, value, role):
        return False

