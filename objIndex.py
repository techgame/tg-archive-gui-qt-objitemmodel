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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectCollectionEntry(object):
    __slots__ = ('item', 'collection')

    parent = None
    def __init__(self, item, collection=None):
        self.item = item
        self.collection = collection

    @classmethod
    def newFlyweight(klass, parent, **ns):
        bklass = getattr(klass, '__flyweight__', klass)
        ns.update(__flyweight__=bklass, parent=weakref.ref(parent))
        return type(bklass)("%s_%s"%(bklass.__name__, id(parent)), (bklass,), ns)

    def getItem(self, oi):
        e = self.item
        if oi and e is not None: 
            e = e.oiUpdate(oi, self.parent)
        return e
    def getCollection(self, oi):
        e = self.collection
        if oi and e is not None: 
            e = e.oiUpdate(oi, self.parent)
        return e
    def getParent(self, oi=None):
        e = self.parent
        if e is not None:
            return e()

    def __len__(self): 
        return 2
    def __iter__(self): 
        yield self.item
        yield self.collection

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectModelIndex(object):
    """Provides a method wrapper around QModelIndex for BaseObjectCollection abstractions.

    This object assumes the QModelIndex's internal pointer is a
    3-entry tuple, whose references are kept is the
    BaseObjectCollection.  It defines basic helper methods based
    on this design.  """
    def __init__(self, mi):
        self.mi = mi
    def __repr__(self):
        if not self:
            return '<oi invalid>'
        return '<oi %s %r>' % (self.rc(), self.item())

    def isObjIndex(self): return True
    def isObjModel(self): return False
    def isObjAdaptor(self): return False
    def isObjCollection(self): return False

    @classmethod
    def fromIndex(klass, index):
        return klass(index)

    def __nonzero__(self):
        return self.mi.isValid()
    def isValid(self):
        return self.mi.isValid()
    def item(self): 
        return self.entry().getItem(self)
    def collection(self): 
        return self.entry().getCollection(self)
    def parent(self):
        return self.entry().getParent(self)

    def entry(self): return self.mi.internalPointer()
    def rc(self): return (self.mi.row(), self.mi.column())
    def row(self): return self.mi.row()
    def column(self): return self.mi.column()
    def model(self): return self.mi.model()

    def oiFindNext(self):
        mi = self.findNext()
        return self.mi.model().asObjIndex(mi)
    def findNext(self):
        mi = self.child()
        if mi.isValid(): 
            return mi
        return self.sibling(1, self.column())

    def child(self, dRow=0, dCol=0):
        model = self.mi.model()
        coll = self.collection()
        if coll is None:
            return model.InvalidIndex()
        return coll.modelIndex(model, dRow, dCol)
    def oiChild(self, dRow=0, dCol=0):
        miChild = self.child(dRow, dCol)
        return self.mi.model().asObjIndex(miChild)

    def sibling(self, dRow=0, dCol=0):
        mi = self.mi
        model = mi.model()
        miParent = self.parent().asModelIndex(model)
        return model.index(mi.row()+dRow, mi.column()+dCol, miParent)
    def oiSibling(self, dRow=0, dCol=0):
        miSib = self.sibling(dRow, dCol)
        return self.mi.model().asObjIndex(miSib)
    def dataChanged(self, dRow=0, dCol=0):
        mi = self.mi
        if dRow or dCol:
            miSib = self.sibling(dRow, dCol)
        else: miSib = self.mi
        return mi.model().dataChanged.emit(mi, miSib)

    def beginInsertRows(self, r0, r1=None):
        return self.mi.model().beginInsertRows(self.mi, r0, r1)
    def endInsertRows(self):
        return self.mi.model().endInsertRows()

    def beginRemoveRows(self, r0, r1=None):
        return self.mi.model().beginRemoveRows(self.mi, r0, r1)
    def endRemoveRows(self):
        return self.mi.model().endRemoveRows()

    def beginMoveRows(self, r0, r1=None):
        return self.mi.model().beginMoveRows(self.mi, r0, r1)
    def endMoveRows(self):
        return self.mi.model().endMoveRows()

    def updateChildren(self):
        self.beginRemoveRows(0,-1)
        self.endRemoveRows()

