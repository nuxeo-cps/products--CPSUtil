"""This is a general script launcher.

For now the options system is at its simplest
"""

import sys
import optparse

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
optparser.add_option('-C', '--conf', dest='zope_conf',
                     help=optparse.SUPPRESS_HELP)
optparser.disable_interspersed_args()

def get_run_function(dotted_name):
    module = __import__(dotted_name)
    for segment in dotted_name.split('.')[1:]:
	module = getattr(module, segment)

    try:
       return module.run
    except AttributeError:
	raise ValueError("Script to be launched must provide a 'run' function")

def get_portal(app, portal_id):
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

def main(options, arguments):
    if not options.zope_conf:
	raise ValueError("Configuration file must be provided")

    Zope2.configure(options.zope_conf)

    # now Zope 2 importer is ready
    run = get_run_function(arguments[1])

    app = Zope2.app()
    portal = get_portal(app, arguments[0])
    login(portal, options.user_id)

    run(portal, arguments[2:])

if __name__ == '__main__':
    options, arguments = optparser.parse_args()
    if len(arguments) < 2:
	optparser.error("Incorrect number of arguments. Use -h for long help")

    del sys.argv[1:] # Zope needs argv to be cleaned up
    # If the launched module uses optparse, will see its dotted name
    # as the prog name (for usage message etc)
    sys.argv[0] = arguments[1]
    main(options, arguments)



