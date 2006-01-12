# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Olivier Grisel <og@nuxeo.com>
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
"""GenericSetup I/O for Zope cache managers
"""
from zope.component import adapts
from zope.interface import implements

from OFS.Cache import isCacheable
from Products.StandardCacheManagers import RAMCacheManager

from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.CPSUtil.interfaces import IRAMCacheManager

class CacheableHelpers:
    """I/O for cache association with Cache Managers
    """
    def _purgeCacheableManagerAssociation(self):
        pass

    def _extractCacheableManagerAssociation(self):
        ob = self.context
        if not isCacheable(ob):
            return
        manager_id = ob.ZCacheable_getManagerId()
        node = self._doc.createElement('cache-manager')
        node.setAttribute('id', str(manager_id))
        return node

    def _initCacheableManagerAssociation(self, node):
        ob = self.context
        if not isCacheable(ob):
            return

        do_set_manager_id = False
        for child in node.childNodes:
            if child.nodeName != 'cache-manager':
                continue
            do_set_manager_id = True
            new_manager_id = child.getAttribute('id')

        if do_set_manager_id:
            if not new_manager_id or new_manager_id == 'None':
                new_manager_id = None
            ob.ZCacheable_invalidate()
            ob.ZCacheable_setManagerId(new_manager_id)

class RAMCacheManagerXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML importer and exporter for RAMCacheManager instances

    RAMCacheManagers are not PropertyManagers so that we cannot directly reuse
    PropertyManagerHelpers methods.
    """

    adapts(IRAMCacheManager, ISetupEnviron)
    implements(IBody)

    _LOGGER_ID = 'ramcachemanager'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractRAMCacheManagerSettings())
        self._logger.info("%r RAM cache manager exported." %
                          self.context.getId())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeRAMCacheManagerSettings()
        self._initRAMCacheManagerSettings(node)
        self._logger.info("%r RAM cache manager imported." %
                          self.context.getId())

    def _extractRAMCacheManagerSettings(self):
        fragment = self._doc.createDocumentFragment()

        # export title first
        node = self._doc.createElement('property')
        node.setAttribute('name', 'title')
        child = self._doc.createTextNode(self.context.title)
        node.appendChild(child)
        fragment.appendChild(node)

        # export settings
        for setting_id, setting_value in self.context._settings.items():
            node = self._doc.createElement('property')
            node.setAttribute('name', setting_id)

            if isinstance(setting_value, (tuple, list)):
                for value in setting_value:
                    child = self._doc.createElement('element')
                    child.setAttribute('value', value)
                    node.appendChild(child)
            else:
                child = self._doc.createTextNode(str(setting_value))
                node.appendChild(child)

            fragment.appendChild(node)
        return fragment

    def _purgeRAMCacheManagerSettings(self):
        RAMCacheManager.caches.clear()
        self.context.__init__(self.context.getId())

    def _initRAMCacheManagerSettings(self, node):
        ob = self.context
        title = ob.title
        new_settings = ob._settings.copy()
        for child in node.childNodes:
            if child.nodeName != 'property':
                continue
            prop_id = str(child.getAttribute('name'))

            if prop_id == 'title':
                title = self._getNodeText(child).encode('utf-8')
                continue

            elements = []
            for sub in child.childNodes:
                if sub.nodeName == 'element':
                    elements.append(sub.getAttribute('value').encode('utf-8'))

            if elements:
                prop_value = tuple(elements) or ()
            else:
                # if we pass a *string* to _updateProperty, all other values
                # are converted to the right type
                prop_value = self._getNodeText(child).encode('utf-8')

            if (not self.environ.shouldPurge()
                and not child.hasAttribute('remove')):
                # If not purge mode and no remove attribute, append to sequence
                prop = ob._settings.get(prop_id)
                if isinstance(prop, (tuple, list)):
                    prop_value = tuple(prop) + tuple(prop_value)

            new_settings[prop_id] = prop_value

        ob.manage_editProps(title, new_settings)


