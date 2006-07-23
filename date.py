# (C) Copyright 2006 Nuxeo SARL <http://nuxeo.com>
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
"""Date utility functions.
"""

import time
from datetime import datetime
from pytz import FixedOffset


def localNow():
    """Get the current datetime with the local timezone.
    """
    if time.localtime()[8]: # DST?
        offset = time.altzone
    else:
        offset = time.timezone
    return datetime.now().replace(tzinfo=FixedOffset(-offset/60))
