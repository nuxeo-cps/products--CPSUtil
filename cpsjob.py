"""This is a general script launcher/helper for CPS.

Can be invocated directly instead of Zope2/Startup/zopectl.py,
or used as a toolkit by zopectl run scripts.
In particular, there is an OptionParser instance and a bootstrap function, to
be used along these lines:

>>> from Products.CPSUtil import cpsjob
>>> cpsjob.optparse.add_option('-e', '--example', dest='exmp'. default='val')
>>> portal, options, arguments = cpsjob.bootstrap(app)

The bootstrap function uses the first positional arg of the script as the name
of the CPS portal. Scripts for which this behaviour would be found useless
or obstrusive can of course import directly some of the lower level helper
functions.

An external method can be applied simply like this:

>>> from Products.CPSUtil import cpsjob
>>> portal, options, arguments = cpsjob.bootstrap(app)
>>> portal.my_external_method()
>>> import transaction; transaction.commit()

Don't forget the commit in this case, since it's usually automatic in the
context external methods are launched in.
"""

import sys
import os
import optparse
import logging

import Zope2

# command line parsing

optparser = optparse.OptionParser(
    usage="usage: %prog [options] <portal id> <job module> [job args]")
optparser.add_option('-u', '--username', dest='user_id', default='cpsjob',
                     help="the identifier of the transient unrestricted "
                     "user to run as (will appear, e.g, in "
                     "status history of modified documents). "
                     "Defaults to '%default'."
                     )
optparser.disable_interspersed_args()

# Taken from ZopeTestCase.
# Not imported because import as side-effect of switching to testing ZODB
def makerequest(app, stdout=sys.stdout, host=None, port=None):
    '''Wraps the app into a fresh REQUEST.'''
    from ZPublisher.BaseRequest import RequestContainer
    from ZPublisher.Request import Request
    from ZPublisher.Response import Response
    response = Response(stdout=stdout)
    environ = {}
    environ['SERVER_NAME'] = host or 'nohost'
    environ['SERVER_PORT'] = '%d' % (port or 80)
    environ['REQUEST_METHOD'] = 'GET'
    request = Request(sys.stdin, environ, response)
    request._steps = ['noobject'] # Fake a published object
    request['ACTUAL_URL'] = request.get('URL') # Zope 2.7.4

    # set Zope3-style default skin so that the request is usable for
    # Zope3-style view look-ups
    from zope.app.publication.browser import setDefaultSkin
    setDefaultSkin(request)

    return app.__of__(RequestContainer(REQUEST=request))


def get_run_function(dotted_name):
    module = __import__(dotted_name)
    for segment in dotted_name.split('.')[1:]:
	module = getattr(module, segment)

    try:
       return module.run
    except AttributeError:
	raise ValueError("Script to be launched must provide a 'run' function")

def get_portal(app, portal_id):
    app = makerequest(app)
    from Products.CPSCore.portal import CPSSite
    try:
        return getattr(app, portal_id)
    except AttributeError:
        found = False
    else:
        found = True

    if not found or not isinstance(portal, CPSSite):
        raise RuntimeError("Not the id of a CPS portal : '%s'", portal_id)

def login(portal, user_id, roles=('Manager', 'Member')):
    from AccessControl.SecurityManagement import newSecurityManager
    from Products.CPSCore.CPSMembershipTool import CPSUnrestrictedUser

    user = CPSUnrestrictedUser(user_id, '', roles, '').__of__(portal.acl_users)
    newSecurityManager(None, user)

def configure_logging():
    """Needs INSTANCE_HOME to be set"""

    handler = logging.FileHandler(
        os.path.join(INSTANCE_HOME, 'log', 'cpsjob.log'))

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)-8s %(message)s',
                                  )#datefmt='%a, %d %b %Y %H:%M:%S',)
    handler.setFormatter(formatter)

    for path in ('', 'Products'):
        logger = logging.getLogger(path)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

def main(options, arguments):
    if not options.zope_conf:
	raise ValueError("Configuration file must be provided")

    Zope2.configure(options.zope_conf)
    # now Zope 2 importer is ready
    run = get_run_function(arguments[1])
    portal, options, arguments = bootstrap(Zope2.app())
    run(portal, arguments[2:])

def bootstrap(app):
    """To be launched via zopectl run.

    Return portal, options, positional arguments
    """
    configure_logging()
    options, arguments = optparser.parse_args()
    portal = get_portal(app, arguments[0])
    if len(arguments) < 1:
	optparser.error("Incorrect number of arguments. Use -h for long help")

    login(portal, options.user_id)
    return portal, options, arguments[1:]

if __name__ == '__main__':
    optparser.add_option('-C', '--conf', dest='zope_conf',
                         help=optparse.SUPPRESS_HELP)
    options, arguments = optparser.parse_args()
    if len(arguments) < 2:
	optparser.error("Incorrect number of arguments. Use -h for long help")

    del sys.argv[1:] # Zope needs argv to be cleaned up
    # If the launched module uses optparse, will see its dotted name
    # as the prog name (for usage message etc)
    sys.argv[0] = arguments[1]
    main(options, arguments)



