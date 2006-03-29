# Copyright (c) 2006 Nuxeo SAS <http://nuxeo.com>
# Authors: Georges Racinet <gracinet@nuxeo.com>
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

from zope.interface import implements
from zope.app import zapi

from Acquisition import aq_base

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.context import BaseContext
from Products.GenericSetup.interfaces import IBody, ISetupEnviron

class SimpleContext(BaseContext):
    implements(ISetupEnviron)

class ManageExportView(BrowserView):

    def getXml(self):
        # required by BaseContext (DummyEnviron actually works)
        stool = getToolByName(self.context, 'portal_setup')
        environ = SimpleContext(stool, 'iso-8859-15')

        exporter = zapi.queryMultiAdapter((self.context, environ), IBody)
        body = exporter.body
        return body

    def exportXml(self):
        self.request.RESPONSE.setHeader('Content-Type', 'text/xml')
        return self.getXml()

    def hasPythonExport(self):
        return callable(getattr(aq_base(self.context), 'manage_export'))

    def exportPy(self):
        # We should change the request slightly but who cares?
        return self.context.manage_export(REQUEST=self.request)
