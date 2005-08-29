# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Tarek Ziade <tziade@nuxeo.com>
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
""" ssha digest with salt, compatible with openldap
"""
import sha, random, base64

def sshaDigest(passphrase, salt=None):
    """ returns a ssha digest (sha-1 with salt)

    this can be used to encrypt a passphrase
    using sha-1 encryption, with salt.
    compatible with openldap fields
    >>> res = sshaDigest('xxx')
    >>> len(res)
    46
    >>> res = sshaDigest('xsazdzxx')
    >>> len(res)
    46
    >>> sshaDigest('xxx').startswith('{SSHA}')
    True
    """
    if salt is None:
        salt = ''
        for i in range(8):
            salt += chr(random.randint(0, 255))
    s = sha.sha()
    s.update(passphrase)
    s.update(salt)
    encoded = base64.encodestring(s.digest()+salt).rstrip()
    crypt = '{SSHA}' + encoded
    return crypt

