# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
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

"""Various introspection methods to the current Zope.

This is intended to work for tests that run without a full ZCA configuration.
Doing this here makes only one to maintain accross the major ongoing Zope
migration
"""

import os
from App.version_txt import getZopeVersion
import Products.Five

ZOPE_VERSION = getZopeVersion()
five_path = os.path.split(Products.Five.__file__)[0]
vfile = open(os.path.join(five_path, 'version.txt'))
vstring = vfile.read()
vfile.close()
split = vstring.split()
assert split[0] == 'Five'

FIVE_VERSION = tuple(int(x) for x in split[1].split('.'))
