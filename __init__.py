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

from Products.CMFCore.DirectoryView import registerDirectory

# Making sure that the ModuleSecurityInfo info statements of the following
# modules are taken into account.
import id
import integration
import text
import html
import session
import resourceregistry

registerDirectory('skins', globals())

# for eggification
def initialize(self):
    return "done"

# Enable XML Export tab in ZMI for a few objects by monkey patching

export_option = (
    {'label': 'Export', 'action': 'manage_genericSetupExport.html'},
    )

from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager import AcceleratedHTTPCacheManager

RAMCacheManager.manage_options += export_option
AcceleratedHTTPCacheManager.manage_options += export_option
