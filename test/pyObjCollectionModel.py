#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os, sys, time

from TG.gui.qt.objItemModel.apiQt import QtCore, QtGui, Qt, QVariant
from TG.gui.qt import objItemModel as OIM

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NamespaceEntry(OIM.ObjAdaptor):
    def __init__(self, name, target):
        klass = getattr(target, '__class__', None)
        if klass is not None:
            self.value = '%s (%s)' % (name, target.__class__.__name__)
        else:
            self.value = '%s (%s)' % (name, type(target).__name__)
    def accept(self, v): 
        return v.visitNamespaceEntry(self)

class GroupTitle(OIM.ObjAdaptor):
    def accept(self, v): return v.visitTitle(self)


class Namespace(OIM.ObjCollection):
    ObjectAdaptor = NamespaceEntry

    targetNS = None
    def __init__(self, name, target):
        self.name = name
        self.target = target

        try: targetNS = vars(target)
        except TypeError: self.targetNS = None
        else:
            if targetNS:
                self.targetNS = iter(sorted(targetNS.items()))

        super(Namespace, self).__init__()

    name = None
    def asObjectAdaptor(self):
        if self.name is not None:
            return NamespaceEntry(self.name, self.target)

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
            self.append(Namespace(*e), oi=oi)

        else: 
            self.targetNS = None

        if not self.hasChildren(oi):
            oi.updateChildren()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GroupCollection(OIM.ObjCollection):
    ObjectAdaptor = GroupTitle
    name = None
    def asObjectAdaptor(self):
        if self.name is not None:
            return GroupTitle(self.name)

class ModuleCollection(OIM.ObjCollection):
    ObjectAdaptor = GroupTitle
    name = None
    def asObjectAdaptor(self):
        if self.name is not None:
            return GroupTitle(self.name)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextDocumentDelegate(OIM.ObjectItemDelegate):
    fmt = "<font color='%(color)s'>%(text)s</font)>"
    def paint(self, painter, option, mi):
        oi = self.asObjIndex(mi)

        opt = QtGui.QStyleOptionViewItemV4(option)
        #self.initStyleOption(opt, mi)
        opt.text = ''
        doc = self.asTextDoc(option, oi)

        painter.save()
        style = opt.widget.style()
        style.drawControl(style.CE_ItemViewItem, opt, painter, opt.widget)

        textRect = style.subElementRect(style.SE_ItemViewItemText, opt, opt.widget);
        painter.translate(textRect.topLeft())
        doc.drawContents(painter)

        painter.restore()

    def sizeHint(self, option, mi):
        oi = self.asObjIndex(mi)
        doc = self.asTextDoc(option, oi)
        sz = doc.size()
        sz = QtCore.QSize(sz.width(), sz.height())
        return sz

    def asTextDoc(self, option, oi):
        info = {'text':oi.item().data(oi, Qt.DisplayRole)}

        doc = QtGui.QTextDocument()
        doc.setDefaultFont(option.font)
        pal = option.palette
        if option.state & QtGui.QStyle.State_Selected:
            color = pal.color(pal.HighlightedText)
        else: color = pal.color(pal.Text)
        info['color'] = color.name()
        doc.setHtml(self.fmt % info)
        return doc

class NamespaceDelegate(TextDocumentDelegate):
    pass
class TitleDelegate(TextDocumentDelegate):
    fmt = "<h3><font color='%(color)s'>%(text)s</font)></h3>"


class VisitingDelegate(OIM.ObjectDispatchDelegate):
    def asDelegate(self, mi):
        oi = self.asObjIndex(mi)
        return oi, oi.item().accept(self)

    _d_title = None
    def visitTitle(self, item):
        d = self._d_title
        if d is None:
            d = TitleDelegate()
            self._d_title = d
        return d
    _d_nsEntry = None
    def visitNamespaceEntry(self, item):
        d = self._d_nsEntry
        if d is None:
            d = NamespaceDelegate()
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
        cNS = GroupCollection()
        cNS.name = "Namespaces"
        r = []
        for k, v in sorted(dns.items()):
            coll = ModuleCollection()
            coll.name = k
            coll.extend(Namespace(*e) for e in v)
            r.append(coll)
        cNS.extend(r)

        cPath = GroupCollection()
        cPath.name = "Paths"
        r = []
        for k, v in sorted(dpath.items()):
            coll = ModuleCollection()
            coll.name = k
            coll.extend(Namespace(*e) for e in v)
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

