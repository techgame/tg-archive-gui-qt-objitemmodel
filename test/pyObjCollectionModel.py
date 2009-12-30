#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os, sys, time

from TG.gui.qt.objectItemModel.apiQt import QtCore, QtGui
from TG.gui.qt import objectItemModel as OIM

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NamespaceEntry(OIM.ObjAdaptor):
    def __init__(self, name, target, parent):
        self.value = '%s (%s)' % (name, target.__class__.__name__)
    def accept(self, v): 
        return v.visitNamespaceEntry(self)

class Namespace(OIM.ObjCollectionEx):
    def __init__(self, name, target, parent=None):
        self.name = name
        self.target = target
        self.targetNS = vars(target)
        if self.targetNS:
            self.targetNS = iter(sorted(self.targetNS.items()))
        else: self.targetNS = None

        super(Namespace, self).__init__(parent)

    name = None
    def asItemAdaptor(self, parent):
        if self.name is not None:
            return NamespaceEntry(self.name, self.target, parent)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.target)

    def hasChildren(self, oi=None):
        if self._entryList:
            return True
        return bool(self.targetNS)
    def canFetchMore(self, oi=None):
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

        else: 
            self.targetNS = None

        if not self.hasChildren(oi):
            oi.beginRemoveRows(0,0)
            oi.endRemoveRows()

    def newEntryForData(self, data):
        name, ns = data
        try: 
            vars(ns)
        except TypeError: 
            return (NamespaceEntry(name, ns, self), None)
        else: 
            coll = Namespace(name, ns, self)
            return (coll.asItemAdaptor(self), coll)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GroupTitle(OIM.ObjAdaptor):
    def accept(self, v): return v.visitTitle(self)

class GroupCollection(OIM.ObjCollectionEx):
    name = None
    def asItemAdaptor(self, parent):
        if self.name is not None:
            return GroupTitle(self.name, parent)

class ModuleCollection(OIM.ObjCollectionEx):
    name = None
    def asItemAdaptor(self, parent):
        if self.name is not None:
            return GroupTitle(self.name, parent)
    def newEntryForData(self, data):
        name, ns = data
        assert ns is not None
        coll = Namespace(name, ns, self)
        return (coll.asItemAdaptor(self), coll)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MyNeatStyledDelegate(OIM.ObjectItemDelegate):
    lineHeight = 0
    def paint(self, painter, option, mi):
        painter.save()
        item = self.asObjIndex(mi).item()

        opt = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(opt, mi)
        opt.text = ''

        style = opt.widget.style()
        style.drawControl(style.CE_ItemViewItem, opt, painter, opt.widget)

        textRect = style.subElementRect(style.SE_ItemViewItemText, opt, opt.widget);
        doc = self.asTextDoc(option, item)
        painter.translate(textRect.topLeft())
        doc.drawContents(painter)

        painter.restore()

    def sizeHint(self, option, mi):
        item = self.asObjIndex(mi).item()
        doc = self.asTextDoc(option, item)
        sz = doc.size()
        sz = QtCore.QSize(sz.width(), sz.height()+self.lineHeight*option.fontMetrics.height())
        return sz

    def asTextDoc(self, option, item):
        text = item.data()
        doc = QtGui.QTextDocument()
        doc.setDefaultFont(option.font)
        pal = option.palette
        if option.state & QtGui.QStyle.State_Selected:
            color = pal.color(pal.HighlightedText)
        else: color = pal.color(pal.Text)
        doc.setHtml(self.fmt % (color.name(), text))
        return doc

class NamespaceDelegate(MyNeatStyledDelegate):
    fmt = "<font color='%s'>%s</font)>"
    colorSelected = 'green'
    colorNormal = 'gray'
class TitleDelegate(MyNeatStyledDelegate):
    fmt = "<h3><font color='%s'>%s</font)></h3>"
    colorSelected = 'orange'
    colorNormal = 'black'
    lineHeight = 1.5


class VisitingDelegate(OIM.ObjectDispatchDelegate):
    def asDelegate(self, mi):
        oi = self.asObjIndex(mi)
        return oi, oi.item().accept(self)

    _d_title = None
    def visitTitle(self, item):
        d = self._d_title
        if d is None:
            d = TitleDelegate(self.parent())
            d.setObjectName("titleItem")
            d.setProperty("purpose", "title")
            self._d_title = d
        return d
    _d_nsEntry = None
    def visitNamespaceEntry(self, item):
        d = self._d_nsEntry
        if d is None:
            d = NamespaceDelegate(self.parent())
            d.setObjectName("entryItem")
            d.setProperty("purpose", "entry")
            self._d_nsEntry = d
        return d

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Form(QtGui.QMainWindow):
    def initGui(self):
        dns = {}
        dpath = {}
        for k, v in sys.modules.items():
            if v is None: 
                continue
            p = getattr(v, '__file__', None)
            if p is None: continue

            p = os.path.abspath(p)
            p = os.path.dirname(p)

            ns,sep,rest = k.partition('.')
            if not sep: 
                rest = ns
                ns = '<global>'

            dns.setdefault(ns, []).append((rest,v))
            dpath.setdefault(p, []).append((k,v))

        self.root = GroupCollection()
        cNS = GroupCollection(self.root)
        cNS.name = "Namespaces"
        r = []
        for k, v in sorted(dns.items()):
            coll = ModuleCollection(cNS)
            coll.name = k
            coll.extend(v)
            r.append(coll)
        cNS.extend(r)

        cPath = GroupCollection(self.root)
        cPath.name = "Paths"
        r = []
        for k, v in sorted(dpath.items()):
            coll = ModuleCollection(cPath)
            coll.name = k
            coll.extend(v)
            r.append(coll)
        cPath.extend(r)

        self.root.extend([cNS, cPath])
        self.model = OIM.ObjItemModel(self.root)

        self.view = QtGui.QTreeView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(VisitingDelegate(self.view))
        self.setCentralWidget(self.view)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Constants / Variiables / Etc. 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

css_treeview = '''
QTreeView {
    show-decoration-selected: 1;
}

QTreeView::item {
    border: 1px solid #d9d9d9;
    border-top-color: transparent;
    border-bottom-color: transparent;
}

QTreeView::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
    border: 1px solid #bfcde4;
}

QTreeView::item:selected {
    border: 1px solid #567dbc;
}

QTreeView::item:selected:active{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
}

QTreeView::item:selected:!active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);
}
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv) 
    app.setStyleSheet(css_treeview)
    form = Form()
    form.initGui()
    form.show() 
    form.raise_() 

    sys.exit(app.exec_()) 

