#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from PyQt4.QtCore import Qt, QVariant, QAbstractItemModel, QModelIndex

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseItemCollection(object):
    def parentCollection(self):
        """Returns the parent collection containing this collection.  
        
        Used to resolve parent of a model index"""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def childEntryAtRowCol(self, row, column):
        """Given (row, column), returns a tuple of (item, collection) for that item.  

        Typically, only row is used to resolve down to an item."""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def childRowColumn(self, child):
        """Find the (row, column) for child.  
        
        Used to resolve parent of a model index"""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def isValidRowCol(self, row, col):
        try: self.childEntryAtRowCol(row, col)
        except LookupError: return False
        else: return True

    def childEntryAt(self, oi):
        return self.childEntryAtRowCol(oi.row(), oi.column())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def asModelIndex(self, qItemModel):
        p = self.parentCollection()
        if p is None: 
            return self.newErrIndex()
        return p.modelIndexForChild(qItemModel, self) 
    def modelIndexForChild(self, qItemModel, child):
        res = self.childRowColumn(child)
        if res is None: 
            return self.newErrIndex()
        return self.modelIndex(qItemModel, *res)
    def modelIndex(self, qItemModel, row, col=0):
        if not self.isValidRowCol(row,col):
            return self.newErrIndex()
        return qItemModel.createIndex(row, col, self)
    def newErrIndex(self):
        return QModelIndex()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectModelIndex(object):
    def __init__(self, mi):
        self.mi = mi
    def __repr__(self):
        if not self:
            return '<oi invalid>'
        return '<oi %s %r>' % (self.rc(), self.item())
    def __nonzero__(self):
        return self.mi.isValid()
    def isValid(self):
        return self.mi.isValid()
    def owner(self):
        return self.mi.internalPointer()
    _entry = None
    def entry(self): 
        e = self._entry
        if e is None:
            e = self.owner().childEntryAt(self)
            self._entry = e
        return e
    def item(self): 
        return self.entry()[0]
    def collection(self): 
        return self.entry()[1]

    def rc(self): return (self.mi.row(), self.mi.column())
    def row(self): return self.mi.row()
    def column(self): return self.mi.column()
    def model(self): return self.mi.model()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseCollectionItemModel(QAbstractItemModel):
    asObjIndex = ObjectModelIndex

    def rootCollection(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def parent(self, mi):
        oi = self.asObjIndex(mi)
        if not oi: return QModelIndex()
        return oi.owner().asModelIndex(self)

    def index(self, row, col, miParent):
        oi = self.asObjIndex(miParent)
        if oi: coll = oi.collection()
        else: coll = self.rootCollection()
        return coll.modelIndex(self, row, col)

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

