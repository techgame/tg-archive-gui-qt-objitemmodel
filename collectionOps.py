#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def idxGroups(indexes, delta=1):
    r = []
    iterIdx = iter(indexes)
    for i0 in iterIdx: 
        break
    else: return r

    i1 = i0
    for i in iterIdx:
        if i1+delta == i:
            i1 = i
            continue
        r.append((i0, i1))
        i0 = i1 = i

    r.append((i0, i1))
    return r

class CollectionOpBase(object):
    collection = None
    oi = None

    def __init__(self, collection, oi):
        self.collection = collection
        if oi is not None:
            if not oi.isObjIndex():
                raise ValueError("Expected an object index instance")
            self.oi = oi

    def __enter__(self):
        return self
    def __exit__(self, excType, exc, tb):
        if excType is None:
            self.perform()

    def perform(self):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    # utility to group idx by sequence
    idxGroups = staticmethod(idxGroups)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CollectionChangeOp(CollectionOpBase):
    def __enter__(self):
        self.base = self.collection._entryList
        self.changed = list(self.base)
        return self.changed

    def perform(self):
        base = self.base
        changed = self.changed
        if base == changed: return

        coll = self.collection
        coll.normalizeEntries(changed)
        coll.invalidateCache()

        if self.oi:
            changeMap = dict((e,i) for i,e in enumerate(changed))
            self.doRemovals(base, changeMap)
            self.doAdds(base, changeMap)
            self.doMoves(base, changed, changeMap)
        else:
            base[:] = changed

        coll.invalidateCache()

    def doRemovals(self, base, changeMap):
        removeGrp = (i for i,e in enumerate(base) if e not in changeMap)
        removeGrp = self.idxGroups(removeGrp)[::-1]

        oi = self.oi
        for i0, i1 in removeGrp:
            #elist = base[i0:i1+1]
            oi.beginRemoveRows(i0,i1)
            del base[i0:i1+1]
            oi.endRemoveRows()
        return len(removeGrp)

    def doAdds(self, base, changeMap):
        addMap = changeMap.copy()
        for e in base:
            addMap.pop(e, None)

        addMap = dict((i,e) for e,i in addMap.items())
        addGrp = self.idxGroups(sorted(addMap.keys()))

        oi = self.oi
        for i0, i1 in addGrp:
            elist = [addMap[i] for i in range(i0, i1+1)]
            oi.beginInsertRows(i0,i1)
            base[i0:i0] = elist
            oi.endInsertRows()
        return len(addGrp)

    def doMoves(self, base, changed, changeMap):
        assert len(base) == len(changed)
        col = 0
        fromList = []; toList = []
        M = self.oi.model()
        for i, e in enumerate(base):
            ci = changeMap[e]
            if ci != i:
                fromList.append(M.createIndex(i, col, e))
                toList.append(M.createIndex(ci, col, e))

        if fromList:
            M.layoutAboutToBeChanged()
            base[:] = changed
            M.changePersistentIndexList(fromList, toList)
            M.layoutChanged()

