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

from AccessControl import allow_type, allow_class
from AccessControl import ModuleSecurityInfo
from zLOG import LOG, INFO, DEBUG
from Products.CMFDefault.utils import bodyfinder
import re

# Regexp of the form xxx<body>xxx</body>xxx.
# DOTALL: Make the "." special character match any character at all, including a
# newline; without this flag, "." will match anything except a newline.
html_body_regexp = re.compile('.*<body.*?>(.*)</body>.*',
                              re.DOTALL)

strip_attributes_regexp = re.compile('xml:lang=".*?"\s?',
                                     re.DOTALL)


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
    #html_body = re.sub(html_body_regexp, r'\1', html_content)
    html_body = bodyfinder(html_content)
    html_body = re.sub(strip_attributes_regexp, '', html_body)

    return html_body
