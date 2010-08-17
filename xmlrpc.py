# (C) Copyright 2005-2008 Nuxeo SAS <http://nuxeo.com>
# Authors:
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
"""
    utilities for XML-RPC, used to send
    complex documents over.

    o marshallDocument(document datas) -> xmlrpc dumpable
    o uMarshallDocument(xmlrpc dumpable) -> document datas
"""
import time
from cPickle import dumps, loads

# XXX will use b64encode when under Python 2.4
from base64 import encodestring, decodestring
from xmlrpclib import DateTime as rpcDateTime

from OFS.Image import Image, File # needed to unpickle
from DateTime import DateTime

def marshallDocument(structure):
    if isinstance(structure, list) or isinstance(structure, tuple):
        return map(marshallElement, structure)
    if isinstance(structure, dict):
        for item in structure:
            if item == 'file_text':
                # generated automatically by PortalTransforms
                structure[item] = ''
            else:
                structure[item] = marshallElement(structure[item])
        return structure
    raise NotImplementedError('Type not implemented: %s' % str(type(structure)))

def unMarshallDocument(structure):
    if isinstance(structure, list) or isinstance(structure, tuple):
        return map(unMarshallElement, structure)
    if isinstance(structure, dict):
        for item in structure:
            structure[item] = unMarshallElement(structure[item])
        return structure
    raise NotImplementedError('Type not implemented: %s' % str(type(structure)))

def marshallObject(object):
    """ this is used for safe object transport

    >>> from DateTime import DateTime
    >>> instance = DateTime('01/01/1970')
    >>> instance.e = 2
    >>> stamp, b64 = marshallObject(instance)
    >>> stamp
    'marshalled'
    >>> b64.startswith('KE5pRGF0ZVRpbW')
    True
    """
    string = dumps(object)
    return 'marshalled', encodestring(string)

def unMarshallObject(stamp, data):
    """ this is used for safe object transport

    >>> from DateTime import DateTime
    >>> instance = DateTime('01/01/1970')
    >>> instance.e = 2
    >>> stamp, b64 = marshallObject(instance)
    >>> feedback = unMarshallObject(stamp, b64)
    >>> isinstance(feedback, DateTime)
    True
    >>> feedback.e
    2
    """
    data = decodestring(data)
    return loads(data)

def marshallElement(element, encoding='utf-8'):
    """ maps element to serialize objects

    >>> from DateTime import DateTime
    >>> date = DateTime('01/01/1971')
    >>> date = marshallElement(date)
    >>> date.value
    '19710101T00:00:00'
    """
    if hasattr(element, 'aq_base'):
        element = marshallElement(element.aq_base)
    elif isinstance(element, Image) or isinstance(element, File):
        element = marshallObject(element)
    elif isinstance(element, DateTime):
        element = rpcDateTime(element)
    elif isinstance(element, dict):
        for key in element.keys():
            if key == 'file_text':
                element[key] = ''
            else:
                element[key] = marshallElement(element[key])
    elif isinstance(element, list):
        element = map(marshallElement, element)
    elif isinstance(element, unicode):
        element = element.encode(encoding)
    return element

def isMarshalledObject(element):
    if ((isinstance(element, tuple) or isinstance(element, list)) and
        len(element) == 2):
        return element[0] == 'marshalled'
    else:
        return False

def _RPCDateTime(date, format='%c'):
    string_date = date.value
    current_time = time.strptime(string_date, "%Y%m%dT%H:%M:%S")
    return time.strftime(format, current_time)

def unMarshallElement(element):
    """ unmarshall element

    >>> from DateTime import DateTime
    >>> date = DateTime('01/01/1971')
    >>> date = unMarshallElement(marshallElement(date))
    >>> str(date)
    '1971/01/01'
    """
    if isMarshalledObject(element):
        return unMarshallObject(element[0], element[1])
    if isinstance(element, rpcDateTime):
        element = _RPCDateTime(element)
        return DateTime(element)
    if isinstance(element, tuple):
        return map(unMarshallElement, list(element))
    if isinstance(element, list):
        return map(unMarshallElement, element)
    if isinstance(element, dict):
        for key in element:
            element[key] = unMarshallElement(element[key])
    return element

def toLatin9(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, unicode):
                v = _stringToLatin9(v)
                obj[k] = v
    elif isinstance(obj, unicode):
        obj = _stringToLatin9(obj)
    return obj

def utf8ToUnicode(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                obj[k] = v.decode('utf-8')
    elif isinstance(obj, str):
        obj = obj.decode('utf-8')
    return obj

def _stringToLatin9(s):
    if s is None:
        return None
    else:
        # Replace RIGHT SINGLE QUOTATION MARK (unicode only)
        # by the APOSTROPHE (ascii and latin1).
        # cf. http://www.cl.cam.ac.uk/~mgk25/ucs/quotes.html
        s = s.replace(u'\u2019', u'\u0027')
        #&#8217;
        return s.encode('iso-8859-15', 'ignore')
