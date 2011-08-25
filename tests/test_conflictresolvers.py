import unittest
from Products.CPSUtil import conflictresolvers

DESCA = dict(id='a', meta_type='T')
DESCB = dict(id='b', meta_type='T')
DESCC = dict(id='c', meta_type='T')
DESCD = dict(id='d', meta_type='T')

# children; in practice, would be PersistentReference instances
A = object()
B = object()
C = object()
D = object()

class FolderWithoutConflictTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = conflictresolvers.FolderWithoutConflicts('some_id')

    def test_resolve0(self):
        old = dict(_objects=())
        commited = dict(_objects=(DESCB,), b=B)
        newstate = dict(_objects=(DESCC,), c=C)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, dict(_objects=(DESCB, DESCC), b=B, c=C))

    def test_resolve(self):
        old = dict(_objects=(DESCA,), a=A)
        commited = dict(_objects=(DESCA, DESCB), a=A, b=B)
        newstate = dict(_objects=(DESCA, DESCC), a=A, c=C)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, dict(_objects=(DESCA, DESCB, DESCC),
                                         a=A, b=B, c=C))

    def test_resolve2(self):
        old = dict(_objects=(DESCA, DESCD), a=A, d=D)
        commited = dict(_objects=(DESCA, DESCD, DESCB), a=A, b=B, d=D)
        newstate = dict(_objects=(DESCA, DESCD, DESCC), a=A, c=C, d=D)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, dict(_objects=(DESCA, DESCD, DESCB, DESCC),
                                         a=A, b=B, c=C, d=D))

    def test_resolve3(self):
        old = dict(_objects=(DESCA,), a=A, d=D)
        commited = dict(_objects=(DESCA, DESCD, DESCB), a=A, b=B, d=D)
        newstate = dict(_objects=(DESCA, DESCC), a=A, c=C)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, dict(_objects=(DESCA, DESCD, DESCB, DESCC),
                                         a=A, b=B, c=C, d=D))

    def test_resolve4(self):
        old = dict(_objects=(DESCA,), a=A, d=D, x=1)
        commited = dict(_objects=(DESCA, DESCD, DESCB), a=A, b=B, d=D, x=1)
        newstate = dict(_objects=(DESCA, DESCC), a=A, c=C, x=1)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, dict(_objects=(DESCA, DESCD, DESCB, DESCC),
                                         a=A, b=B, c=C, d=D, x=1))

    def test_not_resolve_added_other_attr(self):
        old = dict(_objects=(DESCA,), a=A)
        commited = dict(_objects=(DESCA, DESCB), a=A, b=B, x=1)
        newstate = dict(_objects=(DESCA, DESCC), a=A, c=C)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, None)

    def test_not_resolve_changed_other_attr(self):
        old = dict(_objects=(DESCA,), a=A, x=0)
        commited = dict(_objects=(DESCA, DESCB), a=A, b=B, x=1)
        newstate = dict(_objects=(DESCA, DESCC), a=A, c=C)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, None)

    def test_not_resolve_order(self):
        old = dict(_objects=(DESCA, DESCD), a=A, d=D)
        commited = dict(_objects=(DESCD, DESCA, DESCB), a=A, b=B, d=D)
        newstate = dict(_objects=(DESCA, DESCD, DESCC), a=A, c=C, d=D)

        resolved = self.folder._p_resolveConflict(old, commited, newstate)
        self.assertEquals(resolved, None)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FolderWithoutConflictTestCase),
        ))

