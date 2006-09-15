# (C) Copyright 2005-2006 Nuxeo SAS <http://nuxeo.com>
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
from xml.sax.saxutils import quoteattr
from HTMLParser import HTMLParser, HTMLParseError

from AccessControl import ModuleSecurityInfo
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


# Inspired from Alex Martelli's "Python Cookbook"
class HTMLSanitizer(HTMLParser):
    """Clean up entered text to avoid dangerous tags like forms, style, etc
    """
    tags_to_keep = ('div', 'p', 'span', 'br', 'hr',
                    'a',
                    'ul', 'ol', 'li',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'em', 'strong',
                    'dl', 'dt', 'dd',
                    'address', 'q', 'blockquote', 'cite', 'abbr', 'acronym',
                    'table', 'thead', 'tbody', 'th', 'tr', 'td', 'hr',
                    )
    tags_empty = ('br', 'hr', 'img', 'input')
    # <b> and <i> are not allowed in XHTML 1.0 Strict, so we replace them with
    # semantical equivalents.
    tag_replacements = {'b': 'strong',
                        'i': 'em',
        }
    attributes_to_keep = ()
    attributes_to_remove = ('style', 'accesskey', 'onclick')

    def __init__(self, tags_to_keep=None,
                 attributes_to_keep=None, attributes_to_remove=None):
        HTMLParser.__init__(self)
        if tags_to_keep is not None:
           self.tags_to_keep = tags_to_keep
        if attributes_to_keep is not None:
            self.attributes_to_keep = attributes_to_keep
        if attributes_to_remove is not None:
            self.attributes_to_remove = attributes_to_remove
        self.result = []
        self.endTagList = []

    def reset(self):
        HTMLParser.reset(self)
        self.result = []
        self.endTagList = []

    def getResult(self):
        self.close()
        self.cleanup()
        return ''.join(self.result)

    def handle_data(self, data):
        self.result.append(data)

    def handle_charref(self, name):
        self.result.append('&#%s' % name)

    def handle_entyref(self, name):
        x = ';' * self.entitydefs.has_key(name)
        self.result.append('&%s%s' % (name, x))

    def handle_starttag(self, tag, attrs):
        """Remove unwanted tag, using tags_to_keep."""
        # First replacing the tag by another one if needed
        tag = self.tag_replacements.get(tag, tag)
        if tag in self.tags_to_keep:
            self.result.append('<%s' % tag)
            for k, v in attrs:
                if self.attributes_to_keep and not k in self.attributes_to_keep:
                    continue
                if self.attributes_to_remove and k in self.attributes_to_remove:
                    continue
                if k[0:2].lower() != 'on' and v[0:10] != 'javascript':
                    self.result.append(' %s="%s"' % (k, v))
            if tag in self.tags_empty:
                self.result.append('/>')
            else:
                self.result.append('>')
                end_tag = '</%s>' % tag
                self.endTagList.insert(0, end_tag)

    def handle_endtag(self, tag):
        # First eplacing the tag by another one if needed
        tag = self.tag_replacements.get(tag, tag)
        if tag in self.tags_to_keep and tag not in self.tags_empty:
            end_tag = '</%s>' % tag
            self.result.append(end_tag)
            if end_tag in self.endTagList:
                self.endTagList.remove(end_tag)

    def cleanup(self):
        """Append missing closing tags"""
        self.result.extend(self.endTagList)


ModuleSecurityInfo('Products.CPSUtil.html').declarePublic('sanitize')
def sanitize(html, tags_to_keep=None, attributes_to_keep=None,
             attributes_to_remove=None):
    """Cleans html"""
    sanitizer = HTMLSanitizer(tags_to_keep,
                              attributes_to_keep,
                              attributes_to_remove,
                              )
    res = html
    try:
        sanitizer.feed(html)
        res = sanitizer.getResult()
    except HTMLParseError, TypeError:
        pass
    return res


ModuleSecurityInfo('Products.CPSUtil.html').declarePublic('renderHtmlTag')
def renderHtmlTag(tagname, **kw):
    """Render an HTML tag."""
    # The "class" key cannot be used since it is a reserved word in python, so
    # to set the "class" attribute one has to specify the "css_class" key.
    if kw.get('css_class'):
        kw['class'] = kw['css_class']
        del kw['css_class']
    if kw.has_key('contents'):
        contents = kw['contents']
        del kw['contents']
    else:
        contents = None
    attrs = []
    for key, value in kw.items():
        if value is None:
            continue
        if key in ('value', 'alt') or value != '':
            attrs.append('%s=%s' % (key, quoteattr(str(value))))
    res = '<%s %s' % (tagname, ' '.join(attrs))
    if contents is not None:
        res += '>%s</%s>' % (contents, tagname)
    elif tagname in ('input', 'img', 'br', 'hr'):
        res += ' />'
    else:
        res += '>'
    return res


