#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os, sys, time
import types

from TG.gui.qt.objItemModel.apiQt import QtCore, QtGui, Qt, QVariant
from TG.gui.qt import objItemModel as OIM

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SimpleEntry(OIM.ObjAdaptor):
    def accept(self, v): 
        return v.visitSimpleEntry(self)
class NamespaceEntry(OIM.ObjAdaptor):
    def __init__(self, name, target):
        self.name = name
        self.setTarget(target)
    def accept(self, v): 
        return v.visitNamespaceEntry(self)

    def setTarget(self, target):
        tgtKlass = type(target)
        self.value = '%s (%s)' % (self.name, tgtKlass.__name__)

class GroupTitle(OIM.ObjAdaptor):
    def accept(self, v): return v.visitTitle(self)


class Namespace(OIM.ObjCollection):
    Adaptor = NamespaceEntry
    factoryMap = {}

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
            return self.Adaptor(self.name, self.target)

    def __repr__(self):
        return "<%s %s>" % (type(self).__name__, self.target)

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

        results = self.buildResults()
        self.assign(results, oi)
        self.targetNS = None

    def buildResults(self):
        results = []
        for name, target in self.targetNS:
            if not self.keepItem(name, target):
                continue

            item = self.fromItem(name, target)
            if item is not None:
                results.append(item)
        return results

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def keepItem(self, name, target):
        return not name.startswith('_')

    @classmethod
    def fromItem(klass, name, target):
        targetKlass = type(target)
        mro = getattr(targetKlass, '__mro__', [targetKlass])

        sentinal = object()
        for K in mro:
            Factory = klass.factoryMap.get(K, sentinal)
            if Factory is not sentinal: 
                break
        else: Factory = Namespace

        if Factory is not None:
            return Factory(name, target)

    @classmethod
    def register(klass, *types):
        klass.factoryMap.update((t,klass) for t in types)

class ModuleNamespace(Namespace):
    def keepItem(self, name, target):
        module = getattr(target, '__module__', None)
        if module is not None:
            return module == self.target.__name__
        return not name.startswith('_')

ModuleNamespace.register(types.ModuleType)

class TypeNamespace(Namespace):
    def keepItem(self, name, target):
        return True

    def buildResults(self):
        results = [
            BaseClassCollection(
                TypeNamespace(e.__name__, e) for e in self.target.__bases__),
            SubClassCollection(
               TypeNamespace(e.__name__, e) for e in self.target.__subclasses__()),
            ]

        #results.extend(Namespace.buildResults(self))
        return results

TypeNamespace.register(types.TypeType, types.ClassType)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ClassCollection(OIM.ObjCollection):
    name = 'Classes'
    def asObjectAdaptor(self):
        return SimpleEntry(self.name)
class SubClassCollection(ClassCollection):
    name = 'Sub Classes'
class BaseClassCollection(ClassCollection):
    name = 'Base Classes'

class GroupCollection(OIM.ObjCollection):
    name = 'Group'
    def asObjectAdaptor(self):
        return GroupTitle(self.name)

class ModuleCollection(OIM.ObjCollection):
    name = 'Modules'
    def asObjectAdaptor(self):
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
        d = oi.item().accept(self)
        if d is None:
            d = self.visitSimpleEntry(oi.item())
        return oi, d

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
    _d_simpleEntry = None
    def visitSimpleEntry(self, item):
        d = self._d_simpleEntry
        if d is None:
            d = TextDocumentDelegate()
            self._d_simpleEntry = d
        return d

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Form(QtGui.QWidget):
    def initGui(self):
        self.resize(960,720)
        self.splitter = splitter = QtGui.QSplitter()
        splitter.setOrientation(Qt.Vertical)

        vl = QtGui.QVBoxLayout()
        self.setLayout(vl)
        vl.addWidget(splitter)

        self.root = GroupCollection()
        self.model = OIM.ObjItemModel(self.root)
        self.selModel = QtGui.QItemSelectionModel(self.model)

        self.treeView = treeView = QtGui.QTreeView()
        treeView.setModel(self.model)
        treeView.setSelectionModel(self.selModel)
        treeView.setItemDelegate(VisitingDelegate(treeView))
        treeView.setAttribute(Qt.WA_MacShowFocusRect, 0)
        treeView.setHeaderHidden(True)
        splitter.addWidget(treeView)
        #vl.addWidget(treeView, 1)

        self.colView = colView = QtGui.QColumnView()
        colView.setModel(self.model)
        colView.setSelectionModel(self.selModel)
        splitter.addWidget(colView)

        btn = QtGui.QPushButton()
        vl.addWidget(btn, 0)
        btn.setText("Refresh")
        btn.clicked.connect(self.refreshContent)
        self.initCollection(self.root)

    def refreshContent(self, *args, **kw):
        self.initCollection(self.root)
    def initCollection(self, root):
        dns = {}
        dpath = {}
        for k, v in sys.modules.items():
            if v is None: 
                continue
            p = getattr(v, '__file__', None)
            if p is None: continue

            p = os.path.abspath(p)
            p = os.path.dirname(p)
            if p.startswith(sys.exec_prefix):
                continue

            ns,sep,rest = k.partition('.')
            if not sep: 
                dns[ns] = v
            dpath.setdefault(p, []).append((k,v))

        cNS = GroupCollection(Namespace.fromItem(k,v) for k, v in sorted(dns.items()))
        cNS.name = "Namespaces"

        cPath = GroupCollection()
        cPath.name = "Paths"
        r = []
        for k, v in sorted(dpath.items()):
            coll = ModuleCollection()
            coll.name = k
            coll.extend(Namespace.fromItem(*e) for e in sorted(v))
            r.append(coll)
        cPath.extend(r)

        root.assign([cNS, cPath], self.model)
        self.model.reset()


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

def showBrowser():
    form = Form()
    form.setStyleSheet(css_treeview)
    form.initGui()
    form.show() 
    form.raise_() 
    return form

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv) 
    form = showBrowser()
    sys.exit(app.exec_()) 

