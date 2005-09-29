# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
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
"""Utility functions for manipulating HTML, XHTML.
"""
import re
import sgmllib
from htmlentitydefs import entitydefs

from AccessControl import ModuleSecurityInfo
from zLOG import LOG, INFO, DEBUG
from Products.CMFDefault.utils import bodyfinder

# Regexp of the form xxx<body>xxx</body>xxx.
# DOTALL: Make the "." special character match any character at all, including a
# newline; without this flag, "." will match anything except a newline.
HTML_BODY_REGEXP = re.compile('.*<body.*?>(.*)</body>.*', re.DOTALL)

STRIP_ATTRIBUTES_REGEXP = re.compile('xml:lang=".*?"\s?', re.DOTALL)


# Allowing this method to be imported in restricted code
ModuleSecurityInfo('Products.CPSUtil.html').declarePublic('getHtmlBody')
def getHtmlBody(html_content):
    """
    Return the content of the <body> tag of an HTML content given as string.

    Example:
    tal:define="getHtmlBody nocall:modules/Products.CPSUtil.html/getHtmlBody"
    """
    # Substituting the <html><body>xxx</body></html> by xxx.
    # This has the effect of getting the content of the <body> tag of an HTML
    # document.
    #html_body = HTML_BODY_REGEXP.sub(r'\1', html_content)
    html_body = bodyfinder(html_content)
    html_body = STRIP_ATTRIBUTES_REGEXP.sub('', html_body)

    return html_body

# inspired from Alex Martelli's "Python Cookbook"
class HTMLSanitizer(sgmllib.SGMLParser):
    """Clean up entered text to avoid dangerous tags like forms, style, etc
    """
    tags_to_keep = ('p', 'br', 'span', 'div', 'ul', 'ol', 'li',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a',
                    'em', 'strong', 'i', 'd', 'dl', 'dd', 'dd',
                    'table', 'tr', 'td', 'b')
    tolerant_tags = ('br', 'p')
    attributes_to_keep = ()
    attributes_to_remove = ('style', 'class', 'accesskey', 'onclick')

    def __init__(self, tags_to_keep=None, attributes_to_keep=None, attributes_to_remove=None):
        sgmllib.SGMLParser.__init__(self)
        if attributes_to_keep:
            self.attributes_to_keep = attributes_to_keep
        if attributes_to_remove:
            self.attributes_to_remove = attributes_to_remove
        if tags_to_keep:
           self.tags_to_keep = tags_to_keep
        self.result = []
        self.endTagList = []

    def handle_data(self, data):
        self.result.append(data)

    def handle_charref(self, name):
        self.result.append('&#%s' % name)

    def handle_entyref(self, name):
        x = ';' * self.entitydefs.has_key(name)
        self.result.append('&%s%s' % (name, x))

    def unknown_starttag(self, tag, attrs):
        """Remove unwanted tag, using tags_to_keep"""
        if tag in self.tags_to_keep:
            self.result.append('<%s' % tag)
            for k, v in attrs:
                if self.attributes_to_keep and not k in self.attributes_to_keep:
                    continue
                if self.attributes_to_remove and k in self.attributes_to_remove:
                    continue
                if k[0:2].lower() != 'on' and v[0:10] != 'javascript':
                    self.result.append(' %s="%s"' % (k, v))
            self.result.append('>')
            if tag not in self.tolerant_tags:
                end_tag = '</%s>' % tag
                self.endTagList.insert(0, end_tag)

    def unknown_endtag(self, tag):
        if tag in self.tags_to_keep:
            end_tag = '</%s>' % tag
            self.result.append(end_tag)
            if end_tag in self.endTagList:
                self.endTagList.remove(end_tag)

    def cleanup(self):
        """Append missing closing tags"""
        self.result.extend(self.endTagList)

ModuleSecurityInfo('Products.CPSUtil.html').declarePublic('sanitize')   
def sanitize(html, tags_to_keep=None):
    """Cleans html"""
    parser = HTMLSanitizer(tags_to_keep)
    parser.feed(html)
    parser.close()
    parser.cleanup()
    return ''.join(parser.result)


