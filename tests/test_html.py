# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Tarek Ziadé <tz@nuxeo.com>
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
from Products.CPSUtil.html import sanitize

class Test(unittest.TestCase):

    def testHtmlSanitizing(self):
        res = sanitize('<html>ftgyuhjik</html>')
        self.assertEquals(res, 'ftgyuhjik')

        res = sanitize('<html>ftg<strong>yuh</strong> jik</html>')
        self.assertEquals(res, 'ftg<strong>yuh</strong> jik')

        res = sanitize('<html>ftg<strong>yuh  </strong>jik</html>')
        self.assertEquals(res, 'ftg<strong>yuh  </strong>jik')

        res = sanitize('yu<script langage="javascript">h</script></c>')
        self.assertEquals(res, 'yuh')

        res = sanitize('dfrtgyhju<span class="myclass">ghj</span>')
        self.assertEquals(res, 'dfrtgyhju<span>ghj</span>')

        res = sanitize('dfrtgyhju<span class="myclass" >ghj</span>')
        self.assertEquals(res, 'dfrtgyhju<span>ghj</span>')

        res = sanitize('debian <div>fsf dfrtgyhju<span class="myclass" >ghj</span></di>')
        self.assertEquals(res, 'debian <div>fsf dfrtgyhju<span>ghj</span></div>')

        res = sanitize('<a href="../../../../../../../view" accesskey="U" title="wii" _base_href="http://localhost:29980/cps2/sections/wii/we/">wii</a>')
        self.assertEquals(res, '<a href="../../../../../../../view" title="wii" _base_href="http://localhost:29980/cps2/sections/wii/we/">wii</a>')

        markup = '<address>Paris</address><blockquote><p>Paix longue</p></blockquote>'
        res = sanitize(markup)
        self.assertEquals(res, markup)

        markup = '<q>Paix courte</q><cite>22.3.4</cite><abbr>CNRS</abbr><acronym>LASER</acronym>'
        res = sanitize(markup)
        self.assertEquals(res, markup)

        # Testing tag replacements
        res = sanitize('ftg<b>yuh</b>jik abcde')
        self.assertEquals(res, 'ftg<strong>yuh</strong>jik abcde')

        res = sanitize('<span>ftg<b>yuh</b>jik abcde')
        self.assertEquals(res, '<span>ftg<strong>yuh</strong>jik abcde</span>')

        res = sanitize('<html>ftg<b>yuh</b>jik</html>')
        self.assertEquals(res, 'ftg<strong>yuh</strong>jik')

        res = sanitize('ftg<i>yuh</i>jik')
        self.assertEquals(res, 'ftg<em>yuh</em>jik')

        res = sanitize('ftg<i>yuh </i>jik')
        self.assertEquals(res, 'ftg<em>yuh </em>jik')

        res = sanitize('ftg<i>  yuh</i>jik')
        self.assertEquals(res, 'ftg<em>  yuh</em>jik')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
