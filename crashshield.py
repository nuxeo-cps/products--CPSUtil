# (C) Copyright 2009 Georges Racinet
# Author: Georges Racinet <georges@racinet.fr>
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

import sys
import inspect
import traceback
import logging

# provides __traceback_info__
from zExceptions.ExceptionFormatter import format_exception
from Acquisition import aq_acquire
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError

from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('Products.CPSSkins.crashshield')

"""Crash shield and error handling for CPSSkins."""

class CrashShieldException(Exception):
    pass

def shield_apply(obj, meth, *args, **kwargs):
    """Shielded application of a method.

    The object can be used as aq context for various logging purposes.

    Any exception except those that have to go through gets catched and
    transformed in CrashShieldException

    The caller can use __traceback_info__ to provide details
    """
    try:
        return getattr(obj, meth)(*args, **kwargs)
    except ConflictError: # must go through
        raise
    except Unauthorized: # must go through except while rendering an error
        if getToolByName(obj, 'portal_themes').isErrorRendering():
            logger.debug("Catched Unauthorized exception while rendering an "
                         "error page")
            raise CrashShieldException() # no logging
        else:
            raise
    except:
        ## Site Error Log
        try:
            error_log = aq_acquire(obj, '__error_log__')
        except AttributeError:
            error_log = None
        if error_log is not None:
            error_log.raising(sys.exc_info())

        ## logging module

        # using just direct caller's traceback info
        # didn't found options in ExceptionFormatter to do this
        cframe = inspect.stack()[1][0]
        tbi = cframe.f_locals.get('__traceback_info__')
        cformatted = traceback.format_list(traceback.extract_stack(cframe, 1))

        # don't dump through logging if error_log is present
        # because it will do it, according to user preference.
        # note that our log line could be not close from the one provided
        # by Site Error Log, which is bad, but acceptable (just 2 lines, and
        # nothing we can't do about it)
        if error_log is None:
            tb = ''.join(format_exception(*sys.exc_info()))
        else:
            tb = ''

        logger.error(
            "exception catched; caller: \n%s    - __traceback_info__: %s\n%s",
                     ''.join(cformatted), tbi, tb)
        raise CrashShieldException()

