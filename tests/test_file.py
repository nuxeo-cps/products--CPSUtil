# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

import unittest

import rfc822
from cStringIO import StringIO
from cgi import FieldStorage
from ZPublisher.HTTPRequest import FileUpload
import cPickle
from OFS.Image import Pdata

from Products.CPSUtil.file import readPdata
from Products.CPSUtil.file import OFSFileIO
from Products.CPSUtil.file import persistentFixup


class FakeOFSFile(object):
    def __init__(self, data):
        self.data = data
        self.size = len(str(data))

class FileTest(unittest.TestCase):

    checks = [
        (0, -1, ['abcdef', 'ghijkl', 'mnopqr']),
        (3, -1, ['def', 'ghijkl', 'mnopqr']),
        (6, -1, ['ghijkl', 'mnopqr']),
        (8, -1, ['ijkl', 'mnopqr']),
        (12, -1, ['mnopqr']),
        (15, -1, ['pqr']),
        (18, -1, []),
        (42, -1, []),
        (0, 18, ['abcdef', 'ghijkl', 'mnopqr']),
        (0, 12, ['abcdef', 'ghijkl']),
        (0, 8, ['abcdef', 'gh']),
        (0, 5, ['abcde']),
        (3, 42, ['def', 'ghijkl', 'mnopqr']),
        (3, 15, ['def', 'ghijkl', 'mnopqr']),
        (3, 12, ['def', 'ghijkl', 'mno']),
        (6, 42, ['ghijkl', 'mnopqr']),
        (6, 12, ['ghijkl', 'mnopqr']),
        (6, 10, ['ghijkl', 'mnop']),
        (8, 42, ['ijkl', 'mnopqr']),
        (8, 10, ['ijkl', 'mnopqr']),
        (8, 8, ['ijkl', 'mnop']),
        (2, 3, ['cde']),
        (8, 3, ['ijk']),
        ]

    def makePdata(self):
        pdata = Pdata('abcdef')
        p2 = Pdata('ghijkl')
        p3 = Pdata('mnopqr')
        pdata.next = p2
        p2.next = p3
        return pdata

    def test_readPdata(self):
        pdata = self.makePdata()
        for pos, n, expected in self.checks:
            res = readPdata(pdata, pos, n)
            self.assertEquals(expected, res, (pos, n, expected, res))

    def checkMisc1(self, ofsfileio):
        for pos, n, expected in self.checks:
            ofsfileio.seek(pos)
            res = ofsfileio.read(n)
            expected = ''.join(expected)
            self.assertEquals(expected, res, (pos, n, expected, res))

    def checkMisc2(self, ofsfileio):
        self.assertEquals(ofsfileio.read(3), 'abc')
        self.assertEquals(ofsfileio.tell(), 3)
        self.assertEquals(ofsfileio.read(4), 'defg')
        self.assertEquals(ofsfileio.tell(), 7)
        self.assertEquals(ofsfileio.read(7), 'hijklmn')
        self.assertEquals(ofsfileio.tell(), 14)
        self.assertEquals(ofsfileio.read(99), 'opqr')
        self.assertEquals(ofsfileio.tell(), 18)
        self.assertEquals(ofsfileio.read(99), '')
        self.assertEquals(ofsfileio.tell(), 18)
        ofsfileio.seek(3)
        self.assertEquals(ofsfileio.tell(), 3)
        self.assertEquals(ofsfileio.read(3), 'def')
        self.assertEquals(ofsfileio.tell(), 6)
        ofsfileio.seek(3, 1)
        self.assertEquals(ofsfileio.tell(), 9)
        self.assertEquals(ofsfileio.read(3), 'jkl')
        ofsfileio.seek(42)
        self.assertEquals(ofsfileio.tell(), 42) # seems to be std behaviour
        ofsfileio.seek(0, 2)
        self.assertEquals(ofsfileio.tell(), 18)

    def test_OFSFileIO_Pdata(self):
        pdata = self.makePdata()
        ofsfileio = OFSFileIO(FakeOFSFile(pdata))
        self.checkMisc1(ofsfileio)
        ofsfileio.seek(0)
        self.checkMisc2(ofsfileio)

    def test_OFSFileIO_str(self):
        data = 'abcdefghijklmnopqr'
        ofsfileio = OFSFileIO(FakeOFSFile(data))
        self.checkMisc1(ofsfileio)
        ofsfileio.seek(0)
        self.checkMisc2(ofsfileio)

class PersistentFixupTest(unittest.TestCase):

    def test_persistentFixup(self):
        ds = {}
        somelist = [4, 5]
        somedict = {1: 2, 3: somelist}
        ds['foo'] = 'bar'
        ds['baz'] = somedict
        # make a FileUpload like ZPublisher does
        # FieldStorage stores to a tmpfile above length 1000
        text = "Some File "*110
        headers = ('Content-Disposition: form-data; filename="afile.txt"\n'
                   'Content-Type: text/plain\n'
                   'Content-Length: %s\n\n' % len(text))
        headers = rfc822.Message(StringIO(headers))
        environ = {'REQUEST_METHOD': 'POST'}
        fs = FieldStorage(fp=StringIO(text), environ=environ, headers=headers)
        fu = FileUpload(fs)
        ds['file'] = fu

        # Initially not picklable
        pickler = cPickle.Pickler(StringIO(), 1)
        self.assertRaises(TypeError, pickler.dump, ds)
        # Fixup
        persistentFixup(ds)
        # Now picklable
        pickler.dump(ds)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileTest))
    suite.addTest(unittest.makeSuite(PersistentFixupTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
