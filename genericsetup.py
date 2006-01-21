# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""Helpers for GenericSetup
"""

import cgi
from TAL.TALDefs import attrEscape
from xml.dom.minidom import Node

from Products.GenericSetup.utils import _LineWrapper
from Products.GenericSetup.utils import _Element


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
