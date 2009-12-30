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
    from PySide.QtCore import Qt, QVariant, QAbstractItemModel, QModelIndex

if PyQt4 is not None:
    from PyQt4.QtCore import Qt, QVariant, QAbstractItemModel, QModelIndex

