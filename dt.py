# (C) Copyright 2010 Georges Racinet
# Authors:
# Georges Racinet <georges@racinet.fr>
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
"""Date & time handling utilities."""

from datetime import datetime, timedelta, tzinfo
from time import localtime
from DateTime import DateTime

ZERO = timedelta(0)

class FixedSecondsTZ(tzinfo):
    def __init__(self, offset):
        """Offset in in seconds after GMT.
        Exmp: GMT+1 in the sense of RFC 822 3600."""
        self.offset = offset

    def utcoffset(self, dt):
        return timedelta(seconds=self.offset)

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return None

def zdt2dt(zdt, naive=False):
    """Convert a DateTime object to a datetime.

    >>> dt = zdt2dt(DateTime('2010/06/25 12:33 GMT+3'))
    >>> dt.isoformat()
    '2010-06-25T12:33:00+03:00'

    DateTime objects always carry timezone information. Optionaly, one
    can request a conversion to a naive datetime object. This is useful for
    interoperability with libraries that don't expect timezone-aware datetime
    instances, since both kinds can't be compared, but should be avoided if
    possible, because of the great confusion it can imply.
    The examples below demonstrate some non-obvious behaviour

    Preparation: let's make the DateTime class believe that the local timezone
    is GMT+1, with GMT+2 daylight saving time (in summer), and see what happens
    >>> save_localzone0 = DateTime._localzone0
    >>> save_localzone1 = DateTime._localzone1
    >>> save_mutipleZones = DateTime._multipleZones
    >>> DateTime._localzone0 = 'GMT+1'
    >>> DateTime._localzone1 = 'GMT+2'
    >>> DateTime._multipleZones = True

    Now a summer date (from another time zone) is delivered in GMT+2
    >>> zdt2dt(DateTime('2010/06/25 12:37 GMT+3'), naive=True)
    datetime.datetime(2010, 6, 25, 11, 37)

    While a winter date is delivered in GMT+1
    >>> zdt2dt(DateTime('2010/02/25 12:37 GMT+3'), naive=True)
    datetime.datetime(2010, 2, 25, 10, 37)

    Restoring true values
    >>> DateTime._localzone0 = save_localzone0
    >>> DateTime._localzone1 = save_localzone1
    >>> DateTime._multipleZones = save_mutipleZones
    """
    if zdt is None:
        return None
    # Daylights can't be known from DateTime
    import pdb; pdb.set_trace()
    if naive:
        return datetime.fromtimestamp(zdt.timeTime())

    return datetime.fromtimestamp(zdt.timeTime(),
                                  FixedSecondsTZ(zdt.tzoffset()))

def dt2zdt(dt):
    """Convert a datetime object to (Zope) DateTime.

    TIME ZONE MATTERS:
    DateTime is always timezone aware. In case the datetime is unaware,
    the local time zone is applied as a
    fixed-offset. This is a lesser evil : it's even worse to consider any
    naive datetime object as implicitely UTC.

    Warning: the doctests below relies on some DateTime internals in order to be
    independent of settings local to the machine running them.

    Time zone aware datetime instances are the simplest
    >>> dt2zdt(datetime(2010, 10, 10, 12, 23, tzinfo=FixedSecondsTZ(-3600)))
    DateTime('2010/10/10 12:23:00 GMT-1')

    DateTime support half-hour time zones, and has millisecond resolution
    >>> dt2zdt(datetime(2010, 10, 10, 12, 23, 17, 567432,
    ...                 tzinfo=FixedSecondsTZ(5400)))
    DateTime('2010/10/10 12:23:17.567 GMT+0130')

    Now let's consider naive datetime instances.
    First, for these examples to run anywhere and anytime on earth
    we have to make DateTime believe that we are in GMT+4,
    independently of local daylight saving policy.
    >>> save_localzone0 = DateTime._localzone0
    >>> DateTime._multipleZones = False
    >>> save_mutipleZones = DateTime._multipleZones
    >>> DateTime._localzone0 = 'GMT+4'

    Now let's go
    >>> dt2zdt(datetime(2013, 4, 7, 11, 20, 5))
    DateTime('2013/04/07 11:20:05 GMT+4')

    DateTime objects have millisecond resolution:
    >>> dt2zdt(datetime(2013, 4, 7, 11, 20, 5, 123790))
    DateTime('2013/04/07 11:20:05.124 GMT+4')

    >>> DateTime._localzone0 = save_localzone0
    >>> DateTime._multipleZones = save_mutipleZones
    """

    if dt is None:
        return None
    off = dt.utcoffset()
    iso = dt.isoformat()
    if off is None:
        # enhanced timetuple with float seconds
        tt = list(dt.timetuple()[:6])
        tt[5] += dt.microsecond/1000000.0
        # will apply local timezone
        return DateTime(*tt)
    return DateTime(dt.isoformat())  # TODO slow implementation
