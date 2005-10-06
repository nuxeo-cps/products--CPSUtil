#!/usr/bin/python
#
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# Julien Anguenot <ja@nuxeo.com>
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
"""A script to perform various housekeeping tasks on CPS by calling Zope through 
HTTPS and optionally.

This script should be used directly on the server running Zope.

Place this script in /etc/cron.daily/, /etc/cron.weekly/, /etc/cron.monthly/
depending on your needs.

Or you can even make it call by adding an entry in /etc/crontab or through the
"crontab -e" command. Really it is up to you.

Starts the pack_zodb script every night at 03h59:
59 3 * * * /usr/local/bin/cps_housekeeping -rlPb > /dev/null 2>&1
"""

import sys
import os
import base64
import urllib2
from time import strftime, gmtime
from optparse import OptionParser

# Default values that correspond to the values found on Debian Sarge systems
DEFAULT_HOST_NAME = 'localhost'
DEFAULT_HOST_PORT = 9673
DEFAULT_INSTANCE_ID = 'cps'
DEFAULT_USER_NAME = 'admin'
DEFAULT_USER_PASSWORD = 'admin'
DEFAULT_HISTORY_DAYS = 0
DEFAULT_ZODB_PATH = '/var/lib/zope2.7/instance/cps/var/Data.fs'
DEFAULT_ZODB_BACKUP_DIR_PATH = '/var/backups/zodb'

ZODB_PACKING_URL_PATTERN = 'http://%s:%s/Control_Panel/Database/manage_pack?days:float=%d'
PURGE_LOCALROLES_URL_PATTERN = "http://%s:%s/%s/portal_membership/manage_purgeLocalRoles"
PURGE_REPOSITORY_URL_PATTERN = "http://%s:%s/%s/portal_repository/manage_purgeDeletedRevisions"
CPS_LOGIN_URL_PATTERN = "http://%s:%s/%s/logged_in"
TIME_FORMAT = '%Y-%m-%d_%H:%M'

def execArgs():
    """Analyze command line arguments.
    """
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option('-v', '--verbose',
                      action='store_true',
                      dest='verbose',
                      default=False,
                      help="Print additional information to stdout.")

    parser.add_option('-n', '--host',
                      action='store',
                      dest='host_name',
                      type='string',
                      metavar='NAME',
                      default=DEFAULT_HOST_NAME,
                      help="Use NAME for the server to connect to. "
                      "Defaults to %s" % DEFAULT_HOST_NAME)

    parser.add_option('-p', '--port',
                      action='store',
                      dest='host_port',
                      type='int',
                      metavar='NUMBER',
                      default=DEFAULT_HOST_PORT,
                      help="Use NUMBER for the server port to use. "
                      "Defaults to %s" % DEFAULT_HOST_PORT)
              
    parser.add_option('-i', '--instance-id',
                      action='store',
                      dest='instance_id',
                      type='string',
                      metavar='ID',
                      default=DEFAULT_INSTANCE_ID,
                      help="Use ID for CPS instance id to use. "
                      "Defaults to %s" % DEFAULT_INSTANCE_ID)

    parser.add_option('-d', '--days',
                      action='store',
                      dest='days',
                      type='float',
                      metavar='NUMBER',
                      default=DEFAULT_HISTORY_DAYS,
                      help="Use NUMBER for the days to keep in history. "
                      "Defaults to %s" % DEFAULT_HISTORY_DAYS)

    parser.add_option('-u', '--user',
                      action='store',
                      dest='user_name',
                      type='string',
                      metavar='NAME',
                      default=DEFAULT_USER_NAME,
                      help="Use NAME for the user name to Zope. "
                      "Defaults to '%s'" % DEFAULT_USER_NAME)

    parser.add_option('-w', '--password',
                      action='store',
                      dest='user_password',
                      type='string',
                      metavar='PASSWORD',
                      default=DEFAULT_USER_PASSWORD,
                      help="Use PASSWORD for the password to Zope. "
                      "Defaults to '%s'" % DEFAULT_USER_PASSWORD)
                      

    parser.add_option('-r', '--purge-repository',
                      action='store_true',
                      dest='purge_repository',
                      default=False,
                      help="Purge the repository to remove orphan documents")
                      
    parser.add_option('-l', '--purge-localroles',
                      action='store_true',
                      dest='purge_localroles',
                      default=False,
                      help="Clean the localroles of deleted members")
                      
    parser.add_option('-P', '--pack-zodb',
                      action='store_true',
                      dest='pack_zodb',
                      default=False,
                      help="Pack the ZODB")

    parser.add_option('-b', '--backup',
                      action='store_true',
                      dest='backup',
                      default=False,
                      help="Backup the ZODB that has just been packed "
                           "using the cp command.")

    parser.add_option('-z', '--zodbfile',
                      action='store',
                      dest='zodbfile_path',
                      type='string',
                      metavar='FILE',
                      default=DEFAULT_ZODB_PATH,
                      help="The FILE path to the ZODB. "
                      "The default is %s" % DEFAULT_ZODB_PATH)

    parser.add_option('-k', '--backupdir',
                      action='store',
                      dest='backupdir_path',
                      type='string',
                      metavar='FILE',
                      default=DEFAULT_ZODB_BACKUP_DIR_PATH,
                      help="The FILE path to the directory used for storing "
                      "ZODB backups. "
                      "The default is %s" % DEFAULT_ZODB_BACKUP_DIR_PATH)

    (options, args) = parser.parse_args()
    global verbose
    verbose = options.verbose
 
    if options.purge_repository:
        url = PURGE_REPOSITORY_URL_PATTERN % (options.host_name,
                                              options.host_port,
                                              options.instance_id)
        call_url(url, options.user_name, options.user_password)
        log("Successfully purged repository on host %s" % options.host_name)

    if options.purge_localroles:
        url = PURGE_LOCALROLES_URL_PATTERN % (options.host_name,
                                              options.host_port,
                                              options.instance_id)
        call_url(url, options.user_name, options.user_password)
        log("Successfully purged localroles on host %s" % options.host_name)

    if options.pack_zodb:
        url = ZODB_PACKING_URL_PATTERN % (options.host_name,
                                          options.host_port,
                                          options.days)
        call_url(url, options.user_name, options.user_password)
        log("Successfully packed ZODB on host %s" % options.host_name)

    if options.backup:
        backupZodb(options.zodbfile_path, options.backupdir_path)
      

def backupZodb(zodb_path, backupdir_path):
    time_string = strftime(TIME_FORMAT, gmtime())
    zodb_backup_path = os.path.join(backupdir_path, time_string)
    command = "cp -p %s %s" % (zodb_path, zodb_backup_path)
    log("command = %s" % command)
    os.system(command)
    
    
def call_url(url, username, password):
    """Call urlopen with forced HTTP Basic Auth header"""
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)
    try:
        urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        if e.code == 401:
            log('Invalid credentials on %s, aborting' % url, True)

        elif e.code == 400:
            # XXX: manage_purgeLocalRoles returns code 400
            return
        else:
            log('Error %d on %s, aborting' % (e.code, url), True)
        sys.exit(1)
    except IOError:
        log('Unable to open %s, aborting' % url, True)
        sys.exit(1)

def log(message, force=False):
    """Log the given message to stderr.
    """
    if force or verbose:
        print >> sys.stderr, message

# Shell conversion
if __name__ == '__main__':
    execArgs()

