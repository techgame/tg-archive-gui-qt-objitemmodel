#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from siteFrameworks import SiteFrameworkFinder
sfFinder = SiteFrameworkFinder()
r = sfFinder.addSiteFramework('AppHostQt')

import os, sys
sys.path.append('.')
sys.path.append(os.path.abspath('..'))

import basicCollectionModel as bcm

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QModelIndex

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ModuleName(bcm.BasicItemAdaptor):
    pass

class Namespace(bcm.BasicItemCollection):
    def __init__(self, target, parent=None):
        self.target = target
        super(Namespace, self).__init__(parent)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.target)

    def hasChildren(self, oi):
        if self._childList:
            return True
        return bool(vars(self.target))
    def canFetchMore(self, oi):
        return True

    _fetched = False
    def fetchMore(self, oi):
        if self._childList:
            return

        ns = vars(self.target).items()
        if ns:
            oi.model().beginInsertRows(oi.mi, 0, len(ns))
            self.extend(sorted(ns))
            oi.model().endInsertRows()

    def newEntryForData(self, data):
        name, ns = data
        item = ModuleName(name, self)
        try: vars(ns)
        except TypeError: coll = None
        else: coll = Namespace(ns, self)
        return (item, coll)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GroupCollection(bcm.BasicItemCollection):
    pass
class ModuleCollection(bcm.BasicItemCollection):
    def newEntryForData(self, data):
        name, ns = data
        item = ModuleName(name, self)
        if ns is not None:
            coll = Namespace(ns, self)
        else: coll = None
        return (item, coll)

class Form(QtGui.QMainWindow):
    def initGui(self):
        d = {}
        for k, v in sys.modules.items():
            if v is None: 
                continue
            p = getattr(v, '__file__', None)
            if p is not None:
                p = os.path.abspath(p)
                p = os.path.dirname(p)

            d.setdefault(p, []).append((k,v))

        self.root = GroupCollection()
        r = {}
        for k, v in sorted(d.items()):
            item = ModuleName(k, self.root)
            coll = ModuleCollection(self.root)
            coll.extend(v)
            r[k] = (item, coll)

        self.root.extendEntries(r.values())

        self.model = bcm.CollectionItemModel(self.root)

        self.view = QtGui.QTreeView()
        self.view.setModel(self.model)
        self.setCentralWidget(self.view)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv) 
    form = Form()
    form.initGui()
    form.show() 
    form.raise_() 

    sys.exit(app.exec_()) 

