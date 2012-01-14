# (C) Copyright 2012 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from Testing.ZopeTestCase import ZopeTestCase

from ZPublisher.HTTPRequest import HTTPRequest
from DateTime.DateTime import DateTime
from Products.CPSUtil import http

class HttpUtilsTestCase(ZopeTestCase):

    def afterSetUp(self):
        self.request = self.app.REQUEST

    def modifiedSince(self, since, lastmod):
        """Set the header in request and call the tested function.

        Almost single point of upgrade for these tests."""
        http.set_if_modified_since_header(self.request, since)
        return http.is_modified_since(self.request, lastmod)

    def assertStatus(self, status):
        self.assertEquals(self.request.RESPONSE.getStatus(), status)

    def failIfStatus(self, status):
        self.failIfEqual(self.request.RESPONSE.getStatus(), status)

    def test_ims(self):
        self.assertTrue(self.modifiedSince(
                'Thu, 22 Oct 2009 07:36:00 GMT', DateTime('2010/01/01')))
        self.failIfStatus(304)

    def test_ims2(self):
        self.assertFalse(self.modifiedSince(
                'Thu, 22 Oct 2009 07:36:00 GMT', DateTime('2009/01/01')))
        self.assertStatus(304)

    def test_ims_malformatted(self):
        self.assertTrue(self.modifiedSince('asdasd', DateTime('2009/01/01')))
        self.failIfStatus(304)

    def test_ims_float(self):
        self.assertTrue(self.modifiedSince(
                'Thu, 22 Oct 2009 07:36:00 GMT', 1326475511.0)) # 2012-11-13
        self.failIfStatus(304)

    def test_ims_float2(self):
        self.assertFalse(self.modifiedSince(
                'Thu, 22 Oct 2013 07:36:00 GMT', 1326475511.0)) # 2012-11-13
        self.assertStatus(304)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(HttpUtilsTestCase)
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
