# (C) Copyright 2007 Nuxeo SAS <http://nuxeo.com>
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

from Products.CPSDefault.tests.CPSTestCase import CPSTestCase
from Products.CPSDefault.tests.CPSTestCase import MANAGER_ID

from Products.CPSUtil.html import htmlToText

class Test(CPSTestCase):
    login_id = MANAGER_ID

    def afterSetUp(self):
        self.login(self.login_id)

    def beforeTearDown(self):
        self.logout()

    def test_htmlToText(self):
        html = '<strong>fevrier</strong> est <em>lancee la celebration ...'
        text = htmlToText(html, self.portal)
        #print text
        self.assert_(text)
        self.assertEquals(text, 'fevrier est lancee la celebration ...')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

