# (C) Copyright 2011 CPS-CMS Community <http://cps-cms.org/>
# Author: Georges Racinet <gracinet@cps-cms.org>
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
from copy import deepcopy
import unittest
from OFS.PropertyManager import PropertyManager
from Products.CPSUtil.property import sync_prop_defs

class TestUpdatePropDef(unittest.TestCase):

    def setUp(self):
        class WithProps(PropertyManager):
            _properties = (dict(id='classprop', type='string',
                                label='somelabel',
                                mode='w'),)
        self.cls = WithProps

    def test_failure(self):
	self.fail("Volontary failure to test the new buildbot on runtests.")

    def test_type_change(self):
        ob = self.cls()
        ob._properties = deepcopy(ob._properties) + (dict(id='newprop'),)
        self.cls._properties[0]['type'] = 'ustring'
        sync_prop_defs(ob)
        self.assertEquals(ob._properties, (
                dict(id='classprop', type='ustring', label='somelabel',
                        mode='w'),
                dict(id='newprop')))

    def test_new_prop(self):
        ob = self.cls()
        ob._properties = deepcopy(ob._properties) + (dict(id='newprop'),)
        self.cls._properties += (dict(id='newclassprop'),)
        sync_prop_defs(ob)
        self.assertEquals(ob._properties, (
                dict(id='classprop', type='string', label='somelabel',
                        mode='w'),
                dict(id='newprop'),
                dict(id='newclassprop'),))



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUpdatePropDef)
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
