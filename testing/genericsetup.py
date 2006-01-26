# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
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
"""Generic Test case for the GenericSetup export/import mechanism
"""

import os
import unittest
from difflib import ndiff
from tarfile import TarFile
from StringIO import StringIO
from Testing import ZopeTestCase
from Products.Five import zcml
from Products.GenericSetup import BASE
from Products.GenericSetup import profile_registry
from Products.CPSCore.setuptool import CPSSetupTool

import Products

# XXX AT: do not use the TarballTester from GenericSetup to avoid taking care
# of blank lines and to get better error messages
class TarballTester:
    """Class defining helper methods to check tarball files
    """

    def _getFileData(self, dir_path, file_path):
        file_path = os.path.join(Products.__path__[0], dir_path, file_path)
        try:
            f = open(file_path, 'r')
        except IOError:
            raise ValueError("file %s not found" % file_path)
        else:
            data = f.read()
            f.close()
        return data

    def _checkTarballItems(self, fileish, toc_list):
        fileish.seek(0L)
        tarfile = TarFile.open('foo.tar.gz', fileobj=fileish, mode='r:gz')
        items = tarfile.getnames()
        items.sort()
        toc_list.sort()
        self.assertEqual(items, toc_list)

    def _checkTarballItemData(self, fileish, entry_name, data):
        fileish.seek(0L)
        tarfile = TarFile.open('foo.tar.gz', fileobj=fileish, mode='r:gz')
        extract = tarfile.extractfile(entry_name)
        found = extract.read()
        # get rid of blank lines
        found = [x for x in found.split('\n') if x.strip()]
        data = [x for x in data.split('\n') if x.strip()]
        try:
            self.assertEqual(found, data)
        except AssertionError:
            msg = 'File %s differs:\n' % entry_name
            # diff is more lisible presenting second item first
            msg += '\n'.join(list(ndiff(data, found)))
            raise AssertionError(msg)


class ExportImportTestCase(ZopeTestCase.ZopeTestCase, TarballTester):
    """Test case pour GenericSetup import/export mechanism
    """

    # fixture

    def afterSetUp(self):
        zcml.load_site()
        self.setRoles(('Manager',))
        # setup the CPS setup tool
        setup_tool = CPSSetupTool()
        setup_tool_id = setup_tool.getId()
        self.folder._setObject(setup_tool_id, setup_tool)
        self.setup_tool = getattr(self.folder, setup_tool_id)

    def beforeTearDown(self):
        del self.app
        del self.folder
        del self.setup_tool
        self.logout()

    # helper methods

    def registerProfile(self, name, title, description, path, product=None,
                        profile_type=BASE, for_=None):
        profile_registry.registerProfile(name, title, description, path,
                                         product, profile_type, for_)

    def clearProfileRegistry(self):
        profile_registry.clear()

    def importProfile(self, profile_id, extension_ids=(), purge_old=None):
        setup_tool = self.setup_tool
        setup_tool.setImportContext('profile-%s' % profile_id)
        setup_tool.runAllImportSteps(purge_old)
        for extension_id in extension_ids:
            setup_tool.setImportContext('profile-%s' % extension_id)
            setup_tool.runAllImportSteps(purge_old)
        setup_tool.setImportContext('profile-%s' % profile_id)

    def _checkExportProfile(self, dir_path, toc_list):
        export = self.setup_tool.runAllExportSteps()
        fileish = StringIO(export['tarball'])
        self._checkTarballItems(fileish, toc_list)
        for entry_name in toc_list:
            data = self._getFileData(dir_path, entry_name)
            self._checkTarballItemData(fileish, entry_name, data)


