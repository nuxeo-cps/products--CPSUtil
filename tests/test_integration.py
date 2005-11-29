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
from Products.CPSUtil.integration import isUserAgentGecko

class Test(unittest.TestCase):

    def test_isProductPresent(self):
        self.assert_(not isProductPresent('Products.CPSCore'))

        ZopeTestCase.installProduct('CPSCore', quiet=1)
        self.assert_(isProductPresent('Products.CPSCore'))

        self.assert_(not isProductPresent('Products.ProductWhichDoesntExist'))


    def test_getProductVersion(self):
        self.assert_(getProductVersion('CPSUtil'))


    def test_userAgentStrings(self):
        for (user_agent, is_msie, is_gecko) in (
            ('MSIE', True, False),
            ('Mozilla/1.0', False, False),
            ('Mozilla/5.001 (windows; U; NT4.0; en-us) Gecko/25250101',
             False, True),
            ('Mozilla/5.001 (Macintosh; N; PPC; ja) Gecko/25250101 MegaCorpBrowser/1.0 (MegaCorp, Inc.)',
             False, True),
            ('Mozilla/9.876 (X11; U; Linux 2.2.12-20 i686, en) Gecko/25250101 Netscape/5.432b1 (C-MindSpring)',
             False, True),
            ('TinyBrowser/2.0 (TinyBrowser Comment) Gecko/20201231',
             False, True),
            ):
            request = {'HTTP_USER_AGENT': user_agent}
            res_is_msie = isUserAgentMsie(request)
            res_is_gecko = isUserAgentGecko(request)
            self.assertEquals(res_is_msie, is_msie,
                              'Failed on MSIE detection with "%s"'
                              % user_agent)
            self.assertEquals(res_is_gecko, is_gecko,
                              'Failed on Gecko detection with "%s"'
                              % user_agent)



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
