# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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

import time
import unittest

from Products.CPSUtil.timeoutcache import getCache
from Products.CPSUtil.timeoutcache import TimeoutCache
from Products.CPSUtil.timeoutcache import resetAllCaches


def sorted(l):
    l = list(l)
    l.sort()
    return l


class TestCacheRegistry(unittest.TestCase):

    def setUp(self):
        resetAllCaches()

    def tearDown(self):
        resetAllCaches()

    def test_getCache(self):
        cache = getCache('key1')
        self.assert_(cache is not None)
        self.assert_(isinstance(cache, TimeoutCache))

        cache2 = getCache('key1')
        self.assert_(cache is cache2)

        cache3 = getCache('blah')
        self.assertNotEquals(cache3, cache)

    def test_tuple_key(self):
        cache = getCache(('key1', 'abc'))
        self.assert_(cache is not None)
        self.assert_(isinstance(cache, TimeoutCache))

        cache2 = getCache(('key1', 'abc'))
        self.assert_(cache is cache2)

        cache3 = getCache(('key1', 'blah'))
        self.assertNotEquals(cache3, cache)

    def test_constructor(self):
        defc = object()
        def constructor():
            return defc

        cache = getCache('key1', constructor)
        self.assertEquals(cache, defc)

        cache = getCache('blah')
        self.assertNotEquals(cache, defc)

        cache2 = getCache('blah', constructor)
        self.assertEquals(cache2, cache)


class TestTimeoutCache(unittest.TestCase):

    def setUp(self):
        self.cache = getCache('somecache')

    def tearDown(self):
        resetAllCaches()

    def test_get(self):
        cache = self.cache
        cache.setTimeout(60)
        t_now = int(time.time()) + 1
        t_old = t_now - 3
        cache['abc'] = 'def'
        cache['foo'] = 'bar'
        self.assertEquals(cache.get('abc'), 'def')
        self.assertEquals(cache.get('foo'), 'bar')
        # check default
        self.assertEquals(cache.get('xyz'), None)
        self.assertEquals(cache.get('xyz', default='123'), '123')
        self.assertEquals(cache.get('abc', default='123'), 'def')
        self.assertEquals(cache.get('foo', default='123'), 'bar')
        # check min date
        self.assertEquals(cache.get('abc', min_date=t_old), 'def')
        self.assertEquals(cache.get('foo', min_date=t_old), 'bar')
        self.assertEquals(cache.get('foo', default='123', min_date=t_now),
                          '123')
        # foo is cleared after a miss
        self.assertEquals(cache.get('foo'), None)

    def test_cache(self):
        cache = self.cache
        self.assertEquals(cache['abc'], None)
        cache['abc'] = 'def'
        cache['foo'] = 'bar'
        self.assertEquals(cache['abc'], 'def')
        self.assertEquals(cache['foo'], 'bar')
        cache['abc'] = 'gh'
        self.assertEquals(cache['abc'], 'gh')
        del cache['abc']
        self.assertEquals(cache['abc'], None)
        self.assertEquals(cache['foo'], 'bar')
        # Writing again a new value
        cache['foo'] = 'fou'
        self.assertEquals(cache['foo'], 'fou')

    def test_timeout(self):
        cache = self.cache
        cache['abc'] = 'def'
        cache['foo'] = 'bar'
        cache['mom'] = 'mum'
        self.assertEquals(cache['abc'], 'def')
        self.assertEquals(cache['foo'], 'bar')
        self.assertEquals(cache['mom'], 'mum')
        self.assertEquals(sorted(cache.keysWithValidity()),
                          [('abc', True), ('foo', True), ('mom', True)])
        cache.setTimeout(2)
        self.assertEquals(sorted(cache.keysWithValidity()),
                          [('abc', True), ('foo', True), ('mom', True)])

        # Make timeouts expire
        time.sleep(3)
        self.assertEquals(sorted(cache.keysWithValidity()),
                          [('abc', False), ('foo', False), ('mom', False)])
        self.assertEquals(cache['abc'], None)
        # All the cache is invalid accessing a key have cleared all entry
        self.assertEquals(sorted(cache.keysWithValidity()),
                          [])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestCacheRegistry),
        unittest.makeSuite(TestTimeoutCache),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
