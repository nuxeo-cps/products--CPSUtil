# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# Andreea Stefanescu <astefanescu@nuxeo.com>
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
"""Utility functions for generating and manipulating IDs, logins and passwords.
"""

from AccessControl import allow_type, allow_class
from AccessControl import ModuleSecurityInfo
import random
from zLOG import LOG, INFO, DEBUG

# This string contain non-misleading characters that can safely be read and used
# by users. Misleading characters include for example the "l" letter that can be
# mistaken as the "1" number, without the "0" number that can be mistaken as the
# "O" letter, etc.
SAFE_CHARS = "-abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ123456789"


def generatePassword(minlen=10, maxlen=20):
    """Generate a readable password.

    Generate a readable password, ie without misleading characters such as the
    "l" letter that can be mistaken as the "1" number, without the "0" number
    that can be mistaken as the "O" letter, etc."""
    password = ""
    password_size = random.randint(minlen, maxlen)
    for i in range(password_size):
        password += random.choice(SAFE_CHARS)
    return password
