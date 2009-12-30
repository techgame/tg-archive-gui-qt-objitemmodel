#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseObjectAdaptor(object):
    def isObjectAdaptor(self): return True
    def isObjectCollection(self): return False

    def flags(self, oi=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def data(self, oi=None, role=None):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def setData(self, oi, value, role):
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BaseObjectCollection(object):
    def isObjectAdaptor(self): return False
    def isObjectCollection(self): return True

    def parentCollection(self):
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

    def asModelIndex(self, qItemModel):
        p = self.parentCollection()
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

