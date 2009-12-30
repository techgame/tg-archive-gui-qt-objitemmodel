##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2010  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try: import PySide
except ImportError: 
    PySide = None

try: import PyQt4
except ImportError: 
    PyQt4 = None
if not PySide and not PyQt4:
    raise ImportError("Could not import PySide or PyQt4")


if PySide is not None:
    from PySide import QtCore, QtGui
    from PySide.QtCore import Qt, QVariant, QAbstractItemModel, QModelIndex

if PyQt4 is not None:
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtCore import Qt, QVariant, QAbstractItemModel, QModelIndex

