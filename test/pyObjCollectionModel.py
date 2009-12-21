#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from siteFrameworks import SiteFrameworkFinder
sfFinder = SiteFrameworkFinder()
r = sfFinder.addSiteFramework('AppHostQt')

import os, sys, time
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
        self.targetNS = vars(target)
        if self.targetNS:
            self.targetNS = iter(sorted(self.targetNS.items()))
        else: self.targetNS = None

        self.target = repr(target)
        super(Namespace, self).__init__(parent)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.target)

    def hasChildren(self, oi):
        if self._entryList:
            return True
        return bool(self.targetNS)
    def canFetchMore(self, oi):
        return bool(self.targetNS)

    _fetched = False
    def fetchMore(self, oi):
        if not self.targetNS:
            return

        for e in self.targetNS:
            if e[0].startswith('_'): 
                continue
            C = len(self._entryList)
            oi.beginInsertRows(C, C)
            self.append(e)
            oi.endInsertRows()

        else: self.targetNS = None

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

