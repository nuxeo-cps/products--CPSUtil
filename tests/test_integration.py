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
from Testing import ZopeTestCase
from Products.CPSUtil.integration import isProductPresent
from Products.CPSUtil.integration import getProductVersion
from Products.CPSUtil.integration import isUserAgentMsie

class Test(unittest.TestCase):

    def test_isProductPresent(self):
        self.assert_(not isProductPresent('Products.Epoz'))
        self.assert_(not isProductPresent('Products.ExternalEditor'))

        ZopeTestCase.installProduct('CPSCore', quiet=1)
        self.assert_(isProductPresent('Products.CPSCore'))

        ZopeTestCase.installProduct('Epoz', quiet=1)
        self.assert_(isProductPresent('Products.Epoz'))

        ZopeTestCase.installProduct('ExternalEditor', quiet=1)
        self.assert_(isProductPresent('Products.ExternalEditor'))

        self.assert_(not isProductPresent('Products.DummyProductWhichDoesntExist'))


    def test_getProductVersion(self):
        self.assert_(getProductVersion('CPSUtil'))


    def test_isUserAgentMsie(self):
        request = {'HTTP_USER_AGENT': "Mozilla/1.0"}
        self.assert_(not isUserAgentMsie(request))
        request = {'HTTP_USER_AGENT': "MSIE"}
        self.assert_(isUserAgentMsie(request))


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
