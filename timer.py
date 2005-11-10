# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
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
"""Simple Timer."""
import sys
from time import time

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
