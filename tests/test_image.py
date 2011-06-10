# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
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
from Testing.ZopeTestCase import doctest

import os
from OFS.Image import Image
from Products.CPSUtil import image

DATA_DIR = os.path.join(os.path.split(__file__)[0], 'data')

class ImageTestCase(unittest.TestCase):

    def test_tiff(self):
        img = open(os.path.join(DATA_DIR, 'test.tif'))
        self.assertEquals(image.geometry(img), (28, 14))

        img = Image('img', 'test.tif', img)
        # forcing content_type because if incorrect, this won't test #2406
        # properly (in unit tests, we often get application/octet-stream
        # and this is enough for the new code to ignore Zope's stored info).
        img.content_type = 'image/tiff'
        self.assertEquals(image.geometry(img), (28, 14))


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('Products.CPSUtil.image'),
        unittest.makeSuite(ImageTestCase),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
