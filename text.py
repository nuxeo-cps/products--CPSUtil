# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
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
"""Utility functions for manipulating texts.
"""

from AccessControl import allow_type, allow_class
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, INFO, DEBUG


def truncateText(text, size=25):
    """Middle truncature."""
    if text is None or len(text) < size:
        return text
    mid_size = (size-3)/2
    return text[:mid_size] + '...' + text[-mid_size:]
