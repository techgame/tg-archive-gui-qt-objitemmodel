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
    def entryAtRowCol(self, row, column):
        """Given (row, column), returns an entry tuple of (item, collection).

        Typically, only row is used to resolve down to an item."""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def rowColEntryForChild(self, child):
        """Find the (row, column, entry) for item or collection child.
        
        Used to resolve parent of a model index"""
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def isValidRowCol(self, row, col):
        try: 
            self.entryAtRowCol(row, col)
            return True
        except LookupError: 
            return False

    def childEntryAt(self, oi):
        return self.entryAtRowCol(oi.row(), oi.column())

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def asModelIndex(self, qItemModel):
        p = self.parentCollection()
        if p is None: 
            return QModelIndex()
        return p.modelIndexForChild(qItemModel, self) 
    def modelIndexForChild(self, qItemModel, child):
        row, col, entry = self.rowColEntryForChild(child)
        if row is None: 
            return QModelIndex()
        return qItemModel.createIndex(row, col, entry)
    def modelIndex(self, qItemModel, row, col=0):
        try: entry = self.entryAtRowCol(row, col)
        except LookupError:
            return QModelIndex()
        return qItemModel.createIndex(row, col, entry)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectModelIndex(object):
    """Provides a method wrapper around QModelIndex for BaseItemCollection abstractions"""
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
    def item(self): 
        entry = self.mi.internalPointer()
        return entry[0]
    def collection(self): 
        entry = self.mi.internalPointer()
        return entry[1]
    def parent(self):
        entry = self.mi.internalPointer()
        return entry[2]()

    def rc(self): return (self.mi.row(), self.mi.column())
    def row(self): return self.mi.row()
    def column(self): return self.mi.column()
    def model(self): return self.mi.model()

    def beginInsertRows(self, r0, r1=None):
        return self.model().beginInsertRows(self.mi, r0, r1)
    def endInsertRows(self):
        return self.model().endInsertRows()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseCollectionItemModel(QAbstractItemModel):
    """Uses BaseItemCollection abstraction to implement parent() and index() methods"""
    asObjIndex = ObjectModelIndex

    def rootCollection(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def parent(self, mi):
        oi = self.asObjIndex(mi)
        parent = oi.parent() if oi else None
        if parent is not None:
            return parent.asModelIndex(self)
        else: return QModelIndex()

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

