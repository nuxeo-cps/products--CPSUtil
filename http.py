# (C) Copyright 2012 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from DateTime.DateTime import DateTime

logger = logging.getLogger(__name__)

def is_modified_since(request, lastmod):
    """Read If-Modified-Since header and compare it to lastmod time.

    Return True iff dt is greater than the header, ie a fresh whole response
    must be cooked by the caller.

    Otherwise set the status to 304 and return False.
    Caller code then typically sets a void body or a very short message.

    lastmod can be a DateTime object, or a float (seconds from epoch in UTC)
    """
    header = request.get_header('If-Modified-Since', None)
    if header is None:
        return True

    #
    # header parsing taken from OFS.Image.File
    #
    header=header.split( ';')[0]
    # Some proxies seem to send invalid date strings for this
    # header. If the date string is not valid, we ignore it
    # rather than raise an error to be generally consistent
    # with common servers such as Apache (which can usually
    # understand the screwy date string as a lucky side effect
    # of the way they parse it).
    # This happens to be what RFC2616 tells us to do in the face of an
    # invalid date.
    try:
        ims = DateTime(header)
    except:
        logger.warn("Couldn't parse If-Modified-Since header: %s", header)
        return True

    if isinstance(lastmod, float):
        ims = ims.timeTime()

    if lastmod <= ims:
        request.RESPONSE.setStatus(304)
        return False

    return True
