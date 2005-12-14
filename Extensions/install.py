# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# -*- coding: ISO-8859-15 -*-
# Author: Tarek Ziadé <tz@nuxeo.com>
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
# $Id:$
"""CPSUtil Installer

Installer/Updater for the CPSUtil component.
"""
from Products.CPSInstaller.CPSInstaller import CPSInstaller

SKINS = {'scriptaculous': 'Products/CPSUtil/skins/scriptaculous'}

class CPSUtilInstaller(CPSInstaller):
    """CPSUtil Installer
    """
    product_name = "CPSUtil"

    def install(self):
        """ Main func """
        self.log("CPSUtil Install / Update ........ [ S T A R T ]")
        self.verifySkins(SKINS)
        self.resetSkinCache()
        self.finalize()
        self.log("CPSUtil Install / Update .........[ S T O P ]  ")

def install(self):
    installer = CPSUtilInstaller(self)
    installer.install()
    return installer.logResult()
