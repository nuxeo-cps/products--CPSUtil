# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
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
"""Utility functions for manipulating text.
"""

import string, codecs

ACCENTED_CHARS_TRANSLATIONS = string.maketrans(
    r"""ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿ""",
    r"""AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy""")

def toAscii(s):
    """Change accented and special characters by ASCII characters."""
    s = s.translate(ACCENTED_CHARS_TRANSLATIONS)
    s = s.replace('Æ', 'AE')
    s = s.replace('æ', 'ae')
    s = s.replace('Œ', 'OE')
    s = s.replace('œ', 'oe')
    s = s.replace('ß', 'ss')
    return s


def truncateText(text, size=25):
    """Middle truncature."""
    if text is None or len(text) < size:
        return text
    mid_size = (size-3)/2
    return text[:mid_size] + '...' + text[-mid_size:]


# This table gives rough latin9 equivalents for Unicode characters coming from
# the MS Windows western charset (cp1522) that won't get directly translated
# to latin9.
# see also http://openweb.eu.org/articles/caracteres_illegaux/

win2latin9_approx = { # below are cp1252 codes
u'\u201a' : u',',    # 0x82 lower single quote
u'\u201e' : u'"',    # 0x84 lower double quote (german?)
u'\u02c6' : u'^',    # 0x88 small upper ^
u'\u2039' : u'<',    # 0x8b small <
u'\u2018' : u'`',    # 0x91 single curly backquote
u'\u2019' : u"'",    # 0x92 single curly quote
u'\u201c' : u'"',    # 0x93 double curly backquote
u'\u201d' : u'"',    # 0x94 double curly quote
u'\u2013' : u'\xad', # 0x96 small dash
u'\u2014' : u'-',    # 0x97 dash
u'\u02dc' : u'~',    # 0x98 upper tilda
u'\u203a' : u'>',    # 0x9b small >
u'\xb4'   : u"'",    # 0xb4 almost horizontal single quote
u'\u2026' : u'...',  # 0x85 dots in one char
}

def winToLatin9_errors(exc):
    """ Fallback by approximation for latin9 encoding of unicode objects.

    Mostly, this is about Unicode objects obtained from MS Windows Western
    Europe strings (codec identifier 'cp1252').

    This works as an error handler (registered at import time of the present
    module).

    An example going all the way from a Windows string

    >>> wintext = 'L\x92apostrophe est jolie \x85'
    >>> unitext = wintext.decode('cp1252')
    >>> unitext
    u'L\u2019apostrophe est jolie \u2026'
    >>> unitext.encode('iso-8859-15', 'latin9_fallback')
    "L'apostrophe est jolie ..."

    >>> u'L\u2019apostrophe'.encode('iso-8859-15', 'latin9_fallback')
    "L'apostrophe"

    >>> u'1 maps to 3\u2026 See ?'.encode('iso-8859-15', 'latin9_fallback')
    '1 maps to 3... See ?'

    If we can't find an approximate equivalent, we fallback to
    xmlcharrefreplace, that all modern browsers can handle:

    >>> u'\u2032'.encode('iso-8859-15', 'latin9_fallback')
    '&#8242;'


    xmlcharrefreplace will be called for any block of non latin9 translatables
    chars once one in the block cannot be approximated.
    >>> u'ab\u2032\u2026cd\u2014'.encode('iso-8859-15', 'latin9_fallback')
    'ab&#8242;&#8230;cd-'

    Cf http://docs.python.org/lib/module-codecs.html#l2h-984) for more on
    Unicode.encode error handlers
    """

    res = u''
    inp = exc.args[1]
    try:
        for i in range(exc.start, exc.end):
            res += win2latin9_approx[inp[i]]
    except KeyError:
        return codecs.lookup_error('xmlcharrefreplace')(exc)
    return res, exc.end # we made at worst one to many mappings



## Register the fallback
codecs.register_error('latin9_fallback', winToLatin9_errors)
