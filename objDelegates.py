##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2009  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from .apiQt import QAbstractItemDelegate, QStyledItemDelegate

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectDispatchDelegate(QAbstractItemDelegate):
    def asObjIndex(self, mi):
        return mi.model().asObjIndex(mi)
    def asDelegate(self, mi):
        oi = self.asObjIndex(mi)
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def paint(self, painter, option, mi):
        oi, dg = self.asDelegate(mi)
        return dg.paint(painter, option, mi)
    def sizeHint(self, option, mi):
        oi, dg = self.asDelegate(mi)
        return dg.sizeHint(option, mi)

    def createEditor(self, parent, option, mi):
        oi, dg = self.asDelegate(mi)
        return dg.createEditor(parent, option, mi)
    def editorEvent(self, event, model, option, mi):
        oi, dg = self.asDelegate(mi)
        return dg.editorEvent(event, model, option, mi)
    def updateEditorGeometry(self, editor, option, mi):
        oi, dg = self.asDelegate(mi)
        return dg.updateEditorGeometry(editor, option, mi)
    
    def setEditorData(self, editor, mi):
        oi, dg = self.asDelegate(mi)
        return dg.setEditorData(editor, mi)
    def setModelData(self, editor, model, mi):
        oi, dg = self.asDelegate(mi)
        return dg.setModelData(editor, model, mi)

ObjDispatchDelegate = ObjectDispatchDelegate

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ObjectItemDelegate(QStyledItemDelegate):
    lineHeight = 0
    def asObjIndex(self, mi):
        return mi.model().asObjIndex(mi)

ObjItemDelegate = ObjectItemDelegate

