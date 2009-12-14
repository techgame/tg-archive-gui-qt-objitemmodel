#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from PyQt4.QtGui import QAbstractItemModel, QModelIndex

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicItemCollection(object):
    def parentCollection(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def childRowColumn(self, child):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def isValidRowCol(self, row, col):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def childEntryAt(self, mi, key=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def childItemAt(self, mi):
        return self.childEntryAt(mi, 0)
    def childCollectionAt(self, mi):
        return self.childEntryAt(mi, 1)

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectModelIndex(object):
    def __init__(self, mi):
        self.mi = mi
    def __nonzero__(self):
        return self.isValid()
    def owner(self):
        return self.mi.internalPointer()
    def entry(self): 
        return self.owner().childEntryAt(self.mi)
    def item(self): 
        return self.owner().childItemAt(self.mi)
    def collection(self): 
        return self.owner().childCollectionAt(self.mi)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicCollectionItemModel(QAbstractItemModel):
    asObjIndex = ObjectModelIndex

    def rootCollection(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def parent(self, midx):
        oi = self.asObjIndex(miParent)
        coll = oi.owner()
        if coll is None:
            return QModelIndex()
        return coll.asModelIndex(self)

    def index(self, row, col, miParent):
        oi = self.asObjIndex(miParent)
        if oi: coll = oi.owner()
        else: coll = self.rootCollection()
        return coll.modelIndex(self, row, col)

