# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
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
"""Utility functions for manipulating texts.
"""

# Broken MS characters and the corresponding UTF8 characters according to openweb:
# http://openweb.eu.org/articles/caracteres_illegaux/

WINCHAR_MAP = {
   0x80: 0x20ac, # euro symbol
   0x81: 0x00,
   0x82: 0x201a, 
   0x83: 0x0192,
   0x84: 0x201e,
   0x85: 0x2026, # ...
   0x86: 0x2020,
   0x87: 0x2021,
   0x88: 0x02c6,
   0x89: 0x2030,
   0x8a: 0x0160,
   0x8b: 0x2039,
   0x8c: 0x0152,
   0x8d: 0x00,
   0x8e: 0x017d,
   0x8f: 0x00,
   0x90: 0x00,
   0x91: 0x2018,
   0x92: 0x2019, # '
   0x93: 0x201c,
   0x94: 0x201d,
   0x95: 0x2022,
   0x96: 0x2013,
   0x97: 0x2014,
   0x98: 0x02dc,
   0x99: 0x2122,
   0x9a: 0x0161,
   0x9b: 0x203a, # OE
   0x9c: 0x0153, # oe
   0x9d: 0x00,
   0x9e: 0x017e,
   0x9f: 0x0178,
}

def winToUnicode(text):
    """Encode a broken Microsoft Windows encoded string into unicode
    
    Return None for None string for cpsmcat compatibility
    """
    if text is None:
        return None
    if isinstance(text, str):
        text = unicode(text,'latin1')
    return text.translate(WINCHAR_MAP)

def winToLatin9(text, errors='xmlcharrefreplace'):
    """Encode a broken Microsoft Windows encoded string into iso-8859-15

    Take 'xmlcharrefreplace' on default value for errors for modern browser
    Return None for None string for cpsmcat compatibility
    """
    return winToUnicode(text).encode('iso-8859-15', errors)

def truncateText(text, size=25):
    """Middle truncature."""
    if text is None or len(text) < size:
        return text
    mid_size = (size-3)/2
    return text[:mid_size] + '...' + text[-mid_size:]
