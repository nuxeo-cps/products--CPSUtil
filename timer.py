# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Benoit Delbosc <ben@nuxeo.com>
# Tarek Ziadé <tz@nuxeo.com>
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
"""Timers and benching utilities.
"""

import sys
from time import time
from AccessControl import ModuleSecurityInfo

try:
    from zLOG import LOG, DEBUG
except ImportError:
    DEBUG = 'DEBUG'
    def LOG(name, level, message):
        """Log to stdout."""
        sys.stdout.write(level + ' ' + name + ': ' + message + '\n')
        sys.stdout.flush()

class Timer:
    """Very simple timer that output elapsed time in the log.

    >>> from Products.CPSUtil.timer import Timer
    >>> t = Timer('myTimer')
    >>> #do something
    >>> t.mark('something 1')
    >>> #do something
    >>> t.log('something 2')

    will log::

      ... DEBUG Timer myTimer
      ======================== ======= =======
                   something 1  0.873s  51.57%
                   something 2  0.820s  48.43%
      ------------------------ ------- -------
                    Total time  1.693s
      ======================== ======= =======

    """
    def __init__(self, message=None, level=None):
        self.message = message
        if level is None:
            self.level = DEBUG
        else:
            self.level = level
        self.t = []
        self.mark('init')

    def mark(self, mark):
        """Add a marker."""
        self.t.append((time(), mark))

    def __repr__(self):
        t = self.t[:]
        if len(t) < 2:
            return self.message or 'no marker'
        deco = '%30s ======= =======' % ('=' * 25)
        text = [self.message or '']
        text.append(deco)
        x = t.pop(0)
        total = t[-1][0] - x[0]
        while t:
            y = t.pop(0)
            dt = y[0]-x[0]
            text.append('%30s %6.3fs %6.2f%%' % (y[1], dt, 100.0*dt/total ))
            x = y
        text.append(deco.replace('=', '-'))
        text.append('%30s %6.3fs' % ('Total time', total))
        text.append(deco)
        return '\n'.join(text)

    def log(self, mark=None):
        """Log all the marks."""
        if mark is not None:
            self.mark(mark)
        LOG('Timer', self.level, str(self))


# TOLERANCE in Pystones
kPS = 1000
TOLERANCE = 0.5*kPS

sys_path = sys.path[:]
try:
    # Avoid importing from the test.py in ZOPE_HOME
    import os.path
    zope_home = os.path.abspath(ZOPE_HOME)
    if zope_home in sys.path:
        sys.path.remove(zope_home)
    try:
        from test import pystone
        local_pystones = pystone.pystones()
    except ImportError:
        local_pystones = None
finally:
    sys.path[:] = sys_path


# Allowing this method to be imported in restricted code
ModuleSecurityInfo('Products.CPSUtil.timer').declarePublic('pystoneit')
def pystoneit(function, *args, **kw):
    """Measure an absolute time based on pystone measurement.

    This can be used to bench some code and get a absolute scoring.

    Example of usage:
    >>> from Products.CPSUtil import timer
    >>> timer.local_pystones
    (1.23, 40650.406504065038)
    >>> def o():
    ...     a = ''
    ...     for i in range(50000):
    ...         a = '3' * 10
    ...     return a
    ...
    >>> o()
    '3333333333'
    >>> timer.pystoneit(o)
    2171.3598996304308

    The result can be used in unit test to make assertions
    and prevent performance regressions:

    >>> if timer.pystoneit(o) > 3*timer.kPS:
    ...   raise AssertionError('too slow !')
    ...
    >>> if timer.pystoneit(o) > 2*timer.kPS:
    ...   raise AssertionError('too slow !')
    ...
    Traceback (most recent call last):
    File "<stdin>", line 2, in ?
    AssertionError: too slow !

    Raising an assertion error in Unit tests
    leads to a regular test failure (F)
    """
    if not local_pystones:
        raise Exception("The pystone module is not available. "
                        "Check your Zope instance test module.")
    start_time = time()
    #LOG('pystoneit', TRACE, "function = %s" % str(function))
    try:
        function(*args, **kw)
    finally:
        total_time = time() - start_time
        if total_time == 0:
            pystone_total_time = 0
        else:
            pystone_rate = local_pystones[0] / local_pystones[1]
            pystone_total_time = total_time / pystone_rate
    return pystone_total_time
