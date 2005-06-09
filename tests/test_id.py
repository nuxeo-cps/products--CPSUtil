# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
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
from Products.CPSUtil.id import generatePassword, generateId

class Test(unittest.TestCase):

    def testPassword(self):
        password = generatePassword(min_chars=20, max_chars=30)
        password_length = len(password)
        self.assert_(password_length >= 20 and password_length <= 30)


    def testIdGeneration(self):
        s1 = "C'est l'été !"
        self.assertEquals(generateId(s1), "C-est-l-ete")
        self.assertEquals(generateId(s1, lower=True), "c-est-l-ete")

        s1 = "C'est !!! l'été !!!!"
        self.assertEquals(generateId(s1), "C-est-l-ete")
        self.assertEquals(generateId(s1, lower=True), "c-est-l-ete")


    def testIdDeterminism(self):
        """Test if the generateId() method always return the same id when there
        isn't any container in which objects are created.

        Of course if an Id already exists in a given container, the generateId()
        method does NOT return the same value, since its purpose is to generate
        unique and meaningful Ids in a given container.
        """
        examples = ["We are belong to us",
                    "C'est l'été !",
                    # This kind of string can be found on wiki links
                    "?Mine",
                    "???",
                    "???????????",
                   ]
        for s in examples:
            res1 = generateId(s, container=None)
            res2 = generateId(s, container=None)
            self.assertEquals(res1, res2, "Results differ for string '%s'" % s)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
