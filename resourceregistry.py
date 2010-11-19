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
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('Products.CPSUtil.resourceregistry')

security = ModuleSecurityInfo('Products.CPSUtil.resourceregistry')

_resources = {} # resource id -> definition

REQUEST_REGISTRY_KEY = '_cps_rsrc_registry'

class Resource(object):
    def html(self, **kw):
        raise NotImplementedError

class GlobalMethodResource(Resource):
    """For method (ZPT, .py) based resources.

    The id is deduced from the method name."""

    @classmethod
    def register(cls, method_name):
        rid = ('gmeth', cls.__name__, method_name)
        if rid in _resources:
            return rid
        _resources[rid] = cls(method_name)
        return rid

class HtmlResource(Resource):
    """A resource represented by the html fragment that includes it.

    >>> HtmlResource.register('foo',
    ...    '<script type="text/javascript">foo();</script>')
    >>> _resources['foo'].html()
    '<script type="text/javascript">foo();</script>'
    >>> _resources['foo'].html(base_url='/mycps/')
    '<script type="text/javascript">foo();</script>'
    """
    def __init__(self, html):
        self.fragment = html

    def html(self, **kw):
        """Return appropriate inclusion fragment."""
        return self.fragment

    @classmethod
    def register(cls, rid, fragment):
        if rid in _resources:
            raise ValueError('Existing resource by this id : %r' % rid)
        _resources[rid] = cls(fragment)


class JSGlobalMethodResource(GlobalMethodResource):
    """Represent JavaScript resources that are provided by a portal-wide method

    >>> rid = JSGlobalMethodResource.register('prototype.js')
    >>> _resources[rid].html()
    '<script type="text/javascript" src="prototype.js"></script>'
    >>> _resources[rid].html(base_url='/mycps/')
    '<script type="text/javascript" src="/mycps/prototype.js"></script>'
    """

    template = ('<script type="text/javascript" src="%(base_url)s%(name)s">'
                '</script>')

    def __init__(self, js_method):
        self.meth = js_method

    def html(self, base_url=None):
        if base_url is None:
            base_url = ''
        return self.template % dict(base_url=base_url, name=self.meth)

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
        HTML document.
        """
        cat_req = self.required.get(category, ())
        dumped = self.dumped
        res = []
        for rid in cat_req:
            if rid in dumped:
                continue
            r = _resources.get(rid)
            if r is None:
                logger.warn("Unknow resource id : %r", rid)
            res.append(r.html(base_url=self.base_url))
            dumped.add(rid)
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
