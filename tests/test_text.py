# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
#         Olivier Grisel <og@nuxeo.com>
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
from Products.CPSUtil.text import winToUnicode, winToLatin9

class WindowsBrokenCodesTestCase(unittest.TestCase):
    
    
    def test_string(self):
        
        # from a (windows encoded) string
        res = winToLatin9("L\x92apostrophe")
        self.assertEquals(res, "L&#8217;apostrophe")
        
        res = winToLatin9("3\x8050")
        self.assertEquals(res, "3€50")

        # from unicode
        res = winToLatin9(u"L\x92apostrophe")
        self.assertEquals(res, "L&#8217;apostrophe")
        
        res = winToLatin9(u"3\x8050")
        self.assertEquals(res, "3€50")    
        
        
    def test_unicode(self):
        
        res = winToUnicode(u"L\x92apostrophe")
        self.assertEquals(res, u"L\u2019apostrophe")
        
        res = winToUnicode(u"3\x8050")
        self.assertEquals(res, u"3€50") 
        
    
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WindowsBrokenCodesTestCase),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')