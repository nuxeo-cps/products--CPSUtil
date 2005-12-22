# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
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
"""Session utilities.
"""

from AccessControl import ModuleSecurityInfo
from Acquisition import aq_parent
from Products.Transience.Transience import TransientObjectContainer
from Products.Transience.Transience import getCurrentTimeslice

SESSION = 'SESSION'


_marker = object()

ModuleSecurityInfo('Products.CPSUtil.session').declarePublic('sessionGet')
def sessionGet(request, key, default=_marker):
    """Get a key from the session.

    Returns the default if it's not found.

    Tries to avoid creating the session unnecessarily.
    """
    if sessionHasKey(request, key):
        return request[SESSION][key]
    if default is not _marker:
        return default
    raise KeyError("Session doesn't have %r" % (key,))

def sessionHasKey(request, key):
    """Check if the request's session has a given key

    Tries to avoid creating the session unnecessarily.
    """
    if request is None:
        return False
    session = _getSession(request)
    if session is None:
        return False
    return session.has_key(key)

def _getSession(request):
    """Return the current session if it exists, or None.

    Tries to avoid creating a new session unnecessarily.

    This doesn't "touch" the session (so that it doesn't expire after a
    while), so shouldn't be used if that's important.
    """
    if SESSION in request.other:
        # Session was already accessed
        return request.other[SESSION]
    elif not hasattr(request, '_lazies'):
        # Fake request
        return None
    elif SESSION not in request._lazies:
        # No session data manager set up during traversal
        return None

    # Get the session data manager
    sdm = request._lazies[SESSION].im_self
    bid = sdm.getBrowserIdManager().getBrowserId(create=False)
    if bid is None:
        # No session cookie set up
        return None

    # Get the transient object container
    toc = sdm._getSessionDataContainer()
    if not isinstance(toc, TransientObjectContainer):
        return toc.get(bid)
        # TODO: Splice sdm in the acquisition chain

    # Get the session without moving it to the current timeslice
    session = _getSessionFromContainer(toc, bid)
    if session is None:
        return None
    session = toc._wrap(session)
    # Splice sdm in the acquisition chain
    session = session.__of__(sdm.__of__(aq_parent(session)))
    return session

def _getSessionFromContainer(toc, key):
    """Get session from container, doesn't move it to current timeslice.
    """
    if not toc._timeout_slices:
        # Special case for no timeout value
        bucket = toc._data.get(0)
        return bucket.get(key)
    current_ts = getCurrentTimeslice(toc._period)
    current_slices = toc._getCurrentSlices(current_ts)
    for ts in current_slices:
        bucket = toc._data.get(ts) # ReadConflictError hotspot
        if bucket is not None:
            session = bucket.get(key)
            if session is not None:
                return session
    return None
