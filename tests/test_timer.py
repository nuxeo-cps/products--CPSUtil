# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Benoit Delbosc <ben@nuxeo.com>
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
from Products.CPSUtil.timer import Timer
from Products.CPSUtil import timer

class Test(unittest.TestCase):

    def test_timer(self):
        t = Timer('foo')
        for i in range(10):
            for j in range(200):
                for k in range(300):
                    pass
            t.mark('loop %i' % i)
        #print t
        t.log()


    def test_pystoneit(self):
        try:
            # Only running this test is the pystone module can be used
            from test import pystone
            res = timer.pystoneit(self.dummyMethodToBench)
            isinstance(res, float)
        except ImportError:
            pass


    def dummyMethodToBench(self):
        a = ''
        for i in range(50000):
            a = '3' * 10
        return a


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
