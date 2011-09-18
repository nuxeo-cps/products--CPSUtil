# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""PropertiesPostProcessor

Provide the opportunity to react after a ZMI properties change.
"""

from copy import deepcopy

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ManageProperties
from Products.CMFCore.Expression import Expression

from Products.GenericSetup.utils import PropertyManagerHelpers


class PropertiesPostProcessor(object):
    """
    Provide the opportunity to react after a ZMI properties change.

    _propertiesBaseClass must be set to the class whose code we call
    to the the actual properties change.
    """

    security = ClassSecurityInfo()

    security.declareProtected(ManageProperties, 'manage_editProperties')
    def manage_editProperties(self, REQUEST):
        """Edit object properties via the web.

        Computes internal values for the acls.
        """
        self._propertiesBaseClass.manage_editProperties(self, REQUEST)
        self._postProcessProperties()
        if REQUEST is not None:
            message = "Saved changes."
            # XXX Will be rendered twice but what the heck...
            return self.manage_propertiesForm(self, REQUEST,
                                              manage_tabs_message=message)

    security.declareProtected(ManageProperties, 'manage_changeProperties')
    def manage_changeProperties(self, REQUEST=None, **kw):
        """Change existing object properties.

        Computes internal values for the acls.
        """
        if REQUEST is not None:
            for k, v in REQUEST.items():
                kw[k] = v
        self._propertiesBaseClass.manage_changeProperties(self, **kw)
        self._postProcessProperties()
        if REQUEST is not None:
            message = "Saved changes."
            return self.manage_propertiesForm(self, REQUEST,
                                              manage_tabs_message=message)

    _properties_post_process_split = ()
    _properties_post_process_split_lines = ()
    _properties_post_process_tales = ()

    def _postProcessProperties(self):
        """Post-processing after properties change."""
        # Split each line on some separator
        for attr_lines, attr, sep in self._properties_post_process_split_lines:
            setattr(self, attr, tuple( tuple(i.strip() for i in l.split(sep))
                                       for l in getattr(self, attr_lines)))
        # Split a string on some separator.
        for attr_str, attr, seps in self._properties_post_process_split:
            v = [getattr(self, attr_str)]
            for sep in seps:
                vv = []
                for s in v:
                    vv.extend(s.split(sep))
                v = vv
            v = [s.strip() for s in v]
            v = filter(None, v)
            # XXX this is non idempotent but fixing is dangerous
            setattr(self, attr_str, '; '.join(v))
            setattr(self, attr, v)
        # TALES expression.
        for attr_str, attr in self._properties_post_process_tales:
            p = getattr(self, attr_str).strip()
            if p:
                v = Expression(p)
            else:
                v = None
            setattr(self, attr, v)

InitializeClass(PropertiesPostProcessor)


class PostProcessingPropertyManagerHelpers(PropertyManagerHelpers):
    """PropertyManagerHelpers that post-processes properties
    """
    def _initProperties(self, node):
        super(PostProcessingPropertyManagerHelpers, self)._initProperties(node)
        ob = self.context
        if isinstance(ob, PropertiesPostProcessor):
            ob._postProcessProperties()

def sync_prop_defs(ob):
    """Update instance property definitions from class property definitions.

    Does not remove properties that have been removed from the class
    Needed new properties will be created.
    See #2449.
    """
    if not '_properties' in ob.__dict__:
        # no instance level property definitions
        return

    cls_props = dict( (p['id'], p) for p in ob.__class__._properties)
    def keep_or_update(prop):
        """Return updated prop from class if available, prop itself otherwise.
        """
        return deepcopy(cls_props.get(prop['id'], prop))

    ob._properties = tuple(keep_or_update(prop) for prop in ob._properties)

    # now add new class level properties
    ob_props = set(p['id'] for p in ob._properties)
    ob._properties += tuple(pdef for pid, pdef in cls_props.items()
                            if pid not in ob_props)

    ob._p_changed = 1
