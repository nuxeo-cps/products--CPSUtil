# (C) Copyright 2009 Viral Productions <http://viral-prod.com>
# Author: Georges Racinet <georges.racinet@viral-prod.com>
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
# $Id: ViralProdTool.py 1077 2009-11-27 01:06:05Z joe $from persistent import Persistent

"""Various simple classes that handle write concurrency by resolving conflicts.

Typical application : counting, summing."""

from OFS.SimpleItem import SimpleItem

class IncreasingDateTime(SimpleItem):
    """A DateTime object that resolves conflicts by being always increasing."""

    def set(self, value):
        self.value = value

    def __init__(self, zid, **kw):
        self.value = None # works with max and DateTime ordering
        self._setId(zid)

    def _p_resolveConflict(self, oldState, savedState, newState):
        newState['value'] = max(savedState['value'], newState['value'])
        return newState
