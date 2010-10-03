# (C) Copyright 2010 Georges Racinet 
# Author: Georges Racinet <georges@racinet.fr>
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
from Testing.ZopeTestCase import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('Products.CPSUtil.resourceregistry'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
