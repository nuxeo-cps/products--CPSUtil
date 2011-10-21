import unittest
from DateTime import DateTime
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

class IncreasingDateTimeTestCase(unittest.TestCase):

    def test_repr_str(self):
        dt = DateTime(2011, 10, 21)
        idt = conflictresolvers.IncreasingDateTime('idt').set(dt)
        self.assertEquals(repr(idt), "IncreasingDateTime('2011/10/21')")
        self.assertEquals(str(idt), '2011/10/21')

    def test_comparisons(self):
        d1 = DateTime(2011, 10, 21)
        id1 = conflictresolvers.IncreasingDateTime('id1').set(d1)
        self.assertTrue(id1 > None)
        self.assertTrue(None < id1)
        self.assertEquals(id1, id1)
        self.assertEquals(id1, d1)
        self.assertTrue(id1 >= id1)
        self.assertTrue(id1 <= id1)
        self.assertTrue(id1 >= d1)
        self.assertTrue(id1 <= d1)

        d2 = DateTime(2011, 10, 22)
        id2 = conflictresolvers.IncreasingDateTime('id2').set(d2)
        self.assertNotEqual(d1, id2)
        self.assertNotEqual(id1, id2)

        self.assertTrue(id2 > id1)
        self.assertTrue(id1 < id2)
        self.assertTrue(id2 > d1)
        self.assertTrue(d1 < d2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FolderWithoutConflictTestCase),
        unittest.makeSuite(IncreasingDateTimeTestCase),
        ))

