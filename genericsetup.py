# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# (C) Copyright 2012 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     Florent Guillaume <fg@nuxeo.com>
#     G. Racinet <gracinet@cps-cms.org>
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Helpers for GenericSetup
"""

import cgi

from zope.interface import implements
from zope.tal.taldefs import attrEscape
from xml.dom.minidom import Node

from Acquisition import aq_base

from Products.GenericSetup.utils import _LineWrapper
from Products.GenericSetup.utils import _Element
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers

from Products.CPSUtil.property import PostProcessingPropertyManagerHelpers

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron


class StrictTextElement(_Element):
    """GenericSetup _Element but with stricter text node output.

    Text nodes are exported exactly as is, without added whitespace.
    """

    def writexml(self, writer, indent="", addindent="", newl=""):
        # indent = current indentation
        # addindent = indentation to add to higher levels
        # newl = newline string
        wrapper = _LineWrapper(writer, indent, addindent, newl, 78)
        wrapper.write('<%s' % self.tagName)

        # move 'name', 'meta_type' and 'title' to the top, sort the rest
        attrs = self._get_attributes()
        a_names = attrs.keys()
        a_names.sort()
        for special in ('title', 'meta_type', 'name'):
            if special in a_names:
                a_names.remove(special)
                a_names.insert(0, special)

        for a_name in a_names:
            wrapper.write()
            a_value = attrEscape(attrs[a_name].value)
            wrapper.queue(' %s="%s"' % (a_name, a_value))

        if self.childNodes:
            wrapper.queue('>')
            for node in self.childNodes:
                if node.nodeType == Node.TEXT_NODE:
                    data = cgi.escape(node.data)
                    # Here, simplified output, just queue the data
                    wrapper.queue(data)
                else:
                    wrapper.write('', True)
                    node.writexml(writer, indent+addindent, addindent, newl)
            wrapper.write('</%s>' % self.tagName, True)
        else:
            wrapper.write('/>', True)


def getExactNodeText(node):
    """Get exact node text.

    Doesn't strip spaces.
    Returns unicode.
    """
    texts = []
    for child in node.childNodes:
        if child.nodeName != '#text':
            continue
        texts.append(child.nodeValue)
    return ''.join(texts)

class PropertiesSubObjectsXMLAdapter(XMLAdapterBase,
                                     PostProcessingPropertyManagerHelpers,
                                     ObjectManagerHelpers):

    implements(IBody)

    def __init__(self, context, environ):
        super(PropertiesSubObjectsXMLAdapter, self).__init__(context, environ)
        base = aq_base(context)
        self.name = getattr(base, 'generic_setup_name', 'generic')
        self.LOGGER_ID = getattr(base, 'generic_setup_logger', 'generic')

    def _exportNode(self):
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        self._logger.info("%r tool exported.", self.context)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)
        self._initObjects(node)
        self._logger.info("%r imported.", self.context)

    node = property(_exportNode, _importNode)
