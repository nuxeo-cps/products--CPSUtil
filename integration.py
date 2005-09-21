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
"""Utility functions for integrating other or third-party products.
"""

import os.path
import sys
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, INFO, DEBUG

# Allowing this method to be imported in restricted code
ModuleSecurityInfo('Products.CPSUtil.integration').declarePublic('isProductPresent')
def isProductPresent(product_name):
    """Return whether the product corresponding to the given product name is
    present and ready (not broken) in the current Zope instance.

    Examples:
      * in Python code integration.isProductPresent('Products.ExternalEditor')
      * in ZEXPR modules["Products.CPSUtil.utils"].isProductPresent("Products.ExternalEditor")
    """
    log_key = 'isProductPresent'
    present = product_name in sys.modules
    LOG(log_key, DEBUG, "[%s] present = %s" % (product_name, present))
    return present


class ProductError(Exception):
    pass

# Allowing this method to be imported in restricted code
ModuleSecurityInfo('Products.CPSUtil.integration').declarePublic('getProductVersion')
def getProductVersion(product_name):
    """Return the version of the product corresponding to the given product name.

    This method tries first to read a potential version.txt file, and then a
    potential VERSION file.
    """
    basepath = os.path.join(INSTANCE_HOME, 'Products', product_name)

    fpath = os.path.join(basepath, 'version.txt')
    if os.path.exists(fpath):
        version = open(fpath).readline().strip()
        if not version:
            raise ProductError("No version information available")
        return version

    fpath = os.path.join(basepath, 'VERSION')
    if os.path.exists(fpath):
        for line in file(fpath):
            if line.lower().strip().startswith('pkg_version'):
                version = line.split('=')[1]
                version = version.strip()
                return version
        else:
            raise ProductError("No version information available")

    # No version files at all
    raise ProductError("Cannot find version file")


def isUserAgentMsie(request):
    """Return wether the user agent performing the request is
    an MSIE user agent"""
    user_agent = request.get('HTTP_USER_AGENT')
    if user_agent.find('MSIE') != -1:
        return True
    else:
        return False

