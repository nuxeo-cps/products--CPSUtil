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

    def test_password(self):
        password = generatePassword(min_chars=20, max_chars=30)
        password_length = len(password)
        self.assert_(password_length >= 20 and password_length <= 30)

    def test_id(self):
        s1 = "C'est l'�t� !"
        self.assertEquals(generateId(s1), "C-est-l-ete")
        self.assertEquals(generateId(s1, lower=1), "c-est-l-ete")

        s1 = "C'est !!! l'�t� !!!!"
        self.assertEquals(generateId(s1), "C-est-l-ete")
        self.assertEquals(generateId(s1, lower=1), "c-est-l-ete")


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
