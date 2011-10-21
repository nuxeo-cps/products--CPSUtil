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

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

class IncreasingDateTime(SimpleItem):
    """A DateTime object that resolves conflicts by being always increasing."""

    def set(self, value):
        self.value = value
        return self

    def __init__(self, zid, **kw):
        self.value = None # works with max and DateTime ordering
        self._setId(zid)

    def _p_resolveConflict(self, oldState, savedState, newState):
        newState['value'] = max(savedState['value'], newState['value'])
        return newState

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other

    def __ge__(self, other):
        return self.value >= other

    def __le__(self, other):
        return self.value <= other

_missing = object() # local marker for dict missing values

class FolderWithoutConflicts(Folder):
    """A derivative on Folder that doesn't conflict on child creation.

    Two concurrent transactions can add children at the end of the list.
    The conflict is resolved by putting most recent's after the previous ones.

    This is expected to have better behaviour for small folders than BTrees
    because BTrees can conflict while rebalancing (bucket splitting)

    Caution: heard that this may be make children ordering
    inconsitent among threads/ZEO clients because of ZODB caches,
    so better use in cases where the ordering does not matter so much.
    """

    meta_type = "Folder Without Conflicts"

    def _p_resolveConflict(self, old, committed, newstate):
        """We deal for now with adding at the end only.

        Returning None means that the conflict could not be resolved
        """
        committed_objs = committed['_objects']
        newstate_objs = newstate['_objects']
        old_objs = old['_objects']
        # assert in conflicting states _objects to be an addition to old's
        i = -1
        for i, desc in enumerate(old_objs):
            if committed_objs[i] != desc or newstate_objs[i] != desc:
                return

        # construct the new _objects and record list of accepted added attrs
        added_objs = committed_objs[i+1:] + newstate_objs[i+1:]
        added_attrs = [desc['id'] for desc in added_objs]
        newstate['_objects'] = old_objs + added_objs
        for desc in committed_objs[i+1:]:
            attr = desc['id']
            newstate[attr] = committed[attr]

        changed_attrs = ['_objects']
        # check all other attrs are unchanged in both states
        for state in committed, newstate:
            for attr, value in old.items():
                if (attr not in changed_attrs and
                    state.get(attr, _missing) is not value):
                    return

            for attr in state:
                if attr not in old and attr not in added_attrs:
                    return

        return newstate


InitializeClass(FolderWithoutConflicts)
