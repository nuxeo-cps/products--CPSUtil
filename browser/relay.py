from Products.Five.browser import BrowserView

class AcquiredMethodView(BrowserView):
    """Used to explicitely relay the rendering to acquired methods (skins).

    There are cases with custom traversers that can't use Zope2's acquisition
    system. Instead of converting to proper browser views, one can use this
    class in a view declaration whose name is the same as the method to acquire.

    For an example, see CPSPortlets special traverser."""

    def __call__(self, *a, **kw):
        kw['REQUEST'] = self.request
        return getattr(self.context, str(self.__name__))(*a, **kw)
