# (C) Copyright 2010 Georges Racinet
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
"""resource registries, to track external resources to include in wep pages."""
import logging
from zope.interface import implements
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.utils import getToolByName

from interfaces import IResource

logger = logging.getLogger(__name__)

security = ModuleSecurityInfo(__name__)

_resources = {} # resource id -> definition

REQUEST_REGISTRY_KEY = '_cps_rsrc_registry'

class GlobalMethodResource(object):
    """For method (ZPT, .py) based resources.

    The id is deduced from the method name."""

    def __init__(self, meth, depends=()):
        self.meth = meth
        self.depends = depends

    @classmethod
    def register(cls, method_name, depends=()):
        rid = ('gmeth', cls.__name__, method_name)
        if rid in _resources:
            return rid
        _resources[rid] = cls(method_name, depends=depends)
        return rid

class HtmlResource(object):
    """A resource represented by the html fragment that includes it.

    >>> HtmlResource.register('foo',
    ...    '<script type="text/javascript">foo();</script>')
    >>> _resources['foo'].html()
    '<script type="text/javascript">foo();</script>'
    >>> _resources['foo'].html(base_url='/mycps/')
    '<script type="text/javascript">foo();</script>'
    """

    implements(IResource)

    def __init__(self, rid, html, depends=()):
        self.id = rid
        self.fragment = html
        self.depends = depends

    def html(self, **kw):
        """Return appropriate inclusion fragment."""
        return self.fragment

    @classmethod
    def register(cls, rid, fragment, depends=()):
        if rid in _resources:
            raise ValueError('Existing resource by this id : %r' % rid)
        _resources[rid] = cls(rid, fragment, depends=depends)


class JSGlobalMethodResource(GlobalMethodResource):
    """Represent JavaScript resources that are provided by a portal-wide method

    >>> rid = JSGlobalMethodResource.register('prototype.js')
    >>> _resources[rid].html()
    '<script type="text/javascript" src="prototype.js"></script>'
    >>> _resources[rid].html(base_url='/mycps/')
    '<script type="text/javascript" src="/mycps/prototype.js"></script>'
    """

    implements(IResource)

    template = ('<script type="text/javascript" src="%(base_url)s%(name)s">'
                '</script>')

    def html(self, base_url=None):
        if base_url is None:
            base_url = ''
        return self.template % dict(base_url=base_url, name=self.meth)


def _dump_resource(rid, acc, dumped, base_url=None):
    """Accumulator based dumping of resources.

    Takes care of unicity and dependencies.
    Dumped resources are accumulated in acc (must be a list)
    dumped is a set keeping trace of dumped resources

    >>> HtmlResource.register('r1', '<h1>')
    >>> HtmlResource.register('r2', '<h2>', depends=('r1',))
    >>> HtmlResource.register('r3', '<h3>', depends=('r1',))
    >>> HtmlResource.register('r4', '<h4>', depends=('r2', 'r3'))
    >>> dumped = set()
    >>> acc = []; _dump_resource('r4', acc, dumped); acc
    ['<h1>', '<h2>', '<h3>', '<h4>']

    Redundancy avoidance:
    >>> acc = []; _dump_resource('r4', acc, dumped); acc
    []
    >>> HtmlResource.register('r5', '<h5>', depends=('r2', 'r3'))
    >>> HtmlResource.register('r6', '<h6>', depends=('r5', 'r1'))
    >>> acc = []; _dump_resource('r6', acc, dumped); acc
    ['<h5>', '<h6>']
    >>> dumped = set() # flushing history
    >>> acc = []; _dump_resource('r6', acc, dumped); acc
    ['<h1>', '<h2>', '<h3>', '<h5>', '<h6>']

    There is no protection against loops in this method.
    They produce the maximum recursion RuntimeError.
    TODO add protection in registrations (cheaper to do just once)
    """
    if rid in dumped:
        return
    r = _resources[rid]
    for drid in r.depends:
        if drid not in dumped:
            _dump_resource(drid, acc, dumped, base_url=base_url)
    acc.append(r.html(base_url=base_url))
    dumped.add(rid)


class RequestResourceRegistry(object):
    """Transient, request dependent resource registry.

    Resources are identified by their ids, and stored according to a
    requirement category (widget, portlet, etc.)
    """

    def __init__(self, base_url):
        self.required = {}
        self.dumped = set()
        self.base_url = base_url

    def require(self, resource_id, category=None):
        cat_req = self.required.setdefault(category, set())
        if resource_id not in _resources:
            logger.error("Can't require unknow resource %r", resource_id)
            raise KeyError(resource_id)
        cat_req.add(resource_id)

    def dumpCategory(self, category):
        """Produce HTML code providing all the resources for that category.

        Resources that have already been dumped are *not* included.
        Therefore, the caller must ensure proper inclusion in the final
        HTML document in order not to confuse subsequent calls (for other
        categories, e.g.)
        """
        cat_req = self.required.get(category, set())
        dumped = self.dumped
        base_url = self.base_url
        res = []
        for rid in cat_req:
            try:
                _dump_resource(rid, res, dumped, base_url=base_url)
            except KeyError, e:
                logger.warn("Unknow resource id : %r", str(e))
        return '\n'.join(res)

def require_resource(rid, category=None, context=None):
    """Convenience function."""
    get_request_resource_registry(context).require(rid, category=category)

def get_request_resource_registry(context):
    if context is None:
        raise ValueError("need at least the context")
    request = context.REQUEST

    reg = getattr(request, REQUEST_REGISTRY_KEY, None)
    if reg is None:
        # TODO base_url is also provided by CPSSkins in request
        base_url = getToolByName(context, 'portal_url').getBaseUrl()
        reg = RequestResourceRegistry(base_url=base_url)
        setattr(request, REQUEST_REGISTRY_KEY, reg)
    return reg

security.declarePublic('dump_category')
def dump_category(context, category):
    base_url = getToolByName(context, 'portal_url').getBaseUrl()
    return get_request_resource_registry(context).dumpCategory(category)
