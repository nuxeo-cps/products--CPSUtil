# (C) Copyright 2006-2007 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Olivier Grisel <og@nuxeo.com>
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

from zope.interface import Interface, Attribute
from Products.GenericSetup.interfaces import IBody, ISetupEnviron

class IRAMCacheManager(Interface):
    """Standard Zope RAM Cache Manager.
    """

class IAcceleratedHTTPCacheManager(Interface):
    """Standard Zope Accelerated HTTP Cache Manager.
    """

class IForceBodySetupEnviron(ISetupEnviron):
    """To force body export.

    Used by adapters who don't normally export bodies, just nodes
    Example: widget XML adapter."""

class IResource(Interface):
    """A resource such as javascript, stylesheets"""

    rid = Attribute("""Unique identifier among all known resources.

                       Must be hashable and non iterable.
                    """)

    depends = Attribute(
        """Iterable of other resources that this resource depends on.

        Usually, this means that this resource must been included after them
        Internal ordering of them is respected, too.
        For resources deriving from BaseResource, setting a single string value
        is supported.
        """)

    def html(base_url=None):
        """Produce html code suitable for inclusion in head element.

        base_url is useful in case the inclusion is done by a URI
        specification, and is typically the portal url.
        """
