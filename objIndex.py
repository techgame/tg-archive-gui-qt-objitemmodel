#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
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

    @classmethod
    def fromIndex(klass, index):
        return klass(index)

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

    def sibling(self, dRow=0, dCol=0):
        model = self.model()
        miParent = self.parent().asModelIndex(model)
        return model.index(self.row()+dRow, self.column()+dCol, miParent)
    def oiSibling(self, dRow=0, dCol=0):
        miSib = self.sibling(dRow, dCol)
        return self.model().asObjIndex(miSib)
    def dataChanged(self, dRow=0, dCol=0):
        if dRow or dCol:
            miSib = self.sibling(dRow, dCol)
        else: miSib = self.mi
        return self.model().dataChanged.emit(self.mi, miSib)

    def beginInsertRows(self, r0, r1=None):
        return self.model().beginInsertRows(self.mi, r0, r1)
    def endInsertRows(self):
        return self.model().endInsertRows()

    def beginRemoveRows(self, r0, r1=None):
        return self.model().beginRemoveRows(self.mi, r0, r1)
    def endRemoveRows(self):
        return self.model().endRemoveRows()

