# -*- coding: iso-8859-1 -*-
# (C) Copyright 2005-2008 Nuxeo SAS <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# G. Racinet <georges@racinet.fr>
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

import logging
import string, codecs, re

from ZPublisher import Converters
from AccessControl import ModuleSecurityInfo

# encoding of pre-unicode days. Please import this constant rather than
# use it in the migration code : this will reduce the size of greps for
# harcoded iso-8859-15 occurences
OLD_CPS_ENCODING = 'iso-8859-15'

ACCENTED_CHARS_TRANSLATIONS = string.maketrans(
    r"""ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿ""",
    r"""AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyy""")

ENTITY_RE = re.compile(r'&#(\d+);')

logger = logging.getLogger('Products.CPSUtil.text')

def entity_transcode(match_obj):
    """Replace numeric XML entity by corresponding unicode string."""
    return unichr(int(match_obj.group(1)))

def upgrade_string_unicode(v):
    """Upgrade a single string from older CPS encoding, including entities.

    Indeed such entities are quite common as a result of copy-pasting of non
    iso chars in a <textarea>.
    >>> upgrade_string_unicode('See what I mean &#8230;')
    u'See what I mean \u2026'
    >>> upgrade_string_unicode('&#8230; Abusing of ellipsis &#8230;')
    u'\u2026 Abusing of ellipsis \u2026'

    Having problems with source charset and doctest for this one
    >>> upgrade_string_unicode(
    ...    'Av\xe9 l&#8217;assent !') == u'Av\xe9 l\u2019assent !'
    True
    """
    if not isinstance(v, basestring):
        # can have None (typically from a bad field conf)
        return v # not the job of *this* upgrader

    if isinstance(v, str):
        v = v.decode(OLD_CPS_ENCODING)

    return ENTITY_RE.sub(entity_transcode, v)

def uni_lower(s):
    """Makes unicode lower, whether the input is str or unicode.

    >>> uni_lower('AbC')
    u'abc'
    >>> uni_lower(u'Abb\xc9') == u'abb\xe9'
    True
    """
    if isinstance(s, unicode):
        return s.lower()
    elif isinstance(s, str):
        logger.debug("uni_lower: working on %r with no charset", s)
        return unicode(s).lower()
    elif not isinstance(s, basestring):
        raise ValueError("Expected string input, got %r" % s)

ModuleSecurityInfo('Products.CPSUtil.text').declarePublic('toAscii')
def toAscii(s):
    """Change accented and special characters by ASCII characters.

    >>> toAscii('caf\xe9')
    'cafe'
    >>> toAscii(u'caf\xe9-\u1234')
    'cafe-?'
    """
    if isinstance(s, unicode):
        s = s.encode('iso-8859-15', 'replace')
    s = s.translate(ACCENTED_CHARS_TRANSLATIONS)
    s = s.replace('Æ', 'AE')
    s = s.replace('æ', 'ae')
    s = s.replace('¼', 'OE')
    s = s.replace('½', 'oe')
    s = s.replace('ß', 'ss')
    return s

ModuleSecurityInfo('Products.CPSUtil.text').declarePublic('toLatin9')
def toLatin9(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, unicode):
                v = _unicodeToLatin9(v)
                obj[k] = v
    elif isinstance(obj, unicode):
        obj = _unicodeToLatin9(obj)
    return obj

def _unicodeToLatin9(s):
    if s is None:
        return None
    else:
        # Replace RIGHT SINGLE QUOTATION MARK (unicode only)
        # by the APOSTROPHE (ascii and latin1).
        # cf. http://www.cl.cam.ac.uk/~mgk25/ucs/quotes.html
        s = s.replace(u'\u2019', u'\u0027')
        #&#8217;
        return s.encode('iso-8859-15', 'ignore')

ModuleSecurityInfo('Products.CPSUtil.text').declarePublic('truncateText')
def truncateText(text, size=25):
    """Middle truncature."""
    if text is None or len(text) < size:
        return text
    mid_size = (size - 3) / 2
    return text[:mid_size] + '...' + text[-mid_size:]

def isUtf8(text):
    try:
        text = unicode(text, 'UTF-8', 'strict')
        return True
    except UnicodeDecodeError:
        return False

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
u'\u2022' : u'.',    # bullet
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

codecs.register_error('latin9_fallback', winToLatin9_errors)

ModuleSecurityInfo('Products.CPSUtil.text').declarePublic('get_final_encoding')
def get_final_encoding(context):
    """Return the encoding in which HTML pages are produced.

    context is used for acquisition of the default_charset property.

    The 'default_charset' portal property describes what charset is fed to the
    TAL engine. In case the value is 'unicode', it means that ZPT callers are
    supposed to transmit python unicode strings, and therefore that the final
    encoding is made by the TAL engine, according to the Zope configuration
    setting. This function introspects that, so that it can be used by code
    that doesn't call ZPTs to use the correct encoding.

    >>> class FakePortal:
    ...     pass
    >>> portal = FakePortal()
    >>> portal.default_charset = 'iso-dont-exist'
    >>> get_final_encoding(portal)
    'iso-dont-exist'
    >>> portal.default_charset = 'unicode'

    All we can test here is that there's no error. Value depends on zope.conf
    >>> from_conf = get_final_encoding(portal)
    """

    charset = context.default_charset
    if charset != 'unicode':
        return charset
    # see Zope2.Startup.datatypes
    return Converters.default_encoding

