#!/usr/bin/python
#
# (C) Copyright 2005-2008 Nuxeo SAS <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# Olivier Grisel <og@nuxeo.com>
# Julien Anguenot <ja@nuxeo.com>
# Georges Racinet <georges@racinet.fr>
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

"""A cps job to perform the same tasks as bin/cpshousekeeping."""

import logging
import transaction
from Products.CPSUtil import cpsjob

DEFAULT_ARCHIVED_REVISION_COUNT = 0
DEFAULT_HISTORY_DAYS = 0
DEFAULT_ZODB_PATH = '/usr/local/zope/instance/cps/var/Data.fs'
DEFAULT_ZODB_BACKUP_DIR_PATH = '/var/backups/zodb'
DEFAULT_ZODB_BACKUPS_KEEP_COUNT = 7
DEFAULT_NOTIFICATION_FREQ = None

def setup_optparser(parser=cpsjob.optparser):
    usage = """Usage: %prog [options] <portal id>

Example:
%prog --verbose --user admin --purge-repository --purge-localroles-force --pack-zodb --zodbfile /home/zope/cps/var/Data.fs --backupdir /var/backups/zodb/www.mysite.net cps
    """

    parser.add_option('-v', '--verbose',
                      action='store_true',
                      dest='verbose',
                      default=False,
                      help="Print additional information to stdout. Distinct"
                           "from loglevel, which applies to the log file")

    parser.add_option('-r', '--purge-repository',
                      action='store_true',
                      dest='purge_repository',
                      default=False,
                      help="Purge the repository to remove orphan documents.")

    parser.add_option('-l', '--purge-localroles',
                      action='store_true',
                      dest='purge_localroles',
                      default=False,
                      help="Purge the localroles of deleted members "
                      "recorded as such.")

    parser.add_option('-L', '--purge-localroles-force',
                      action='store_true',
                      dest='purge_localroles_force',
                      default=False,
                      help="Purge the localroles of deleted members.")

    parser.add_option('--purge-archived-revisions',
                      action='store_true',
                      dest='purge_archived_revisions',
                      default=False,
                      help="Purge the archived revisions of documents.")

    parser.add_option('--archived-revisions',
                      action='store',
                      dest='archived_revisions',
                      type='int',
                      metavar='NUMBER',
                      default=DEFAULT_ARCHIVED_REVISION_COUNT,
                      help="Use NUMBER for the number of archives "
                      "to keep for each document. "
                      "Defaults to %s." % DEFAULT_HISTORY_DAYS)

    parser.add_option('-P', '--pack-zodb',
                      action='store_true',
                      dest='pack_zodb',
                      default=False,
                      help="Pack the ZODB.")

    parser.add_option('-d', '--days',
                      action='store',
                      dest='days',
                      type='float',
                      metavar='NUMBER',
                      default=DEFAULT_HISTORY_DAYS,
                      help="Use NUMBER for the days to keep in history. "
                      "Defaults to %s." % DEFAULT_HISTORY_DAYS)

    parser.add_option('-z', '--zodbfile',
                      action='store',
                      dest='zodbfile_path',
                      type='string',
                      metavar='FILE',
                      default=DEFAULT_ZODB_PATH,
                      help="The FILE path to the ZODB. "
                      "The default is %s." % DEFAULT_ZODB_PATH)

    parser.add_option('-b', '--backup',
                      action='store_true',
                      dest='backup',
                      default=False,
                      help="Backup the ZODB that has just been packed "
                      """using the "cp" command.""")

    parser.add_option('-k', '--backupdir',
                      action='store',
                      dest='backupdir_path',
                      type='string',
                      metavar='FILE',
                      default=DEFAULT_ZODB_BACKUP_DIR_PATH,
                      help="The FILE path of the directory used for storing "
                      "ZODB backups. "
                      "The default is %s." % DEFAULT_ZODB_BACKUP_DIR_PATH)

    parser.add_option('--nocompress',
                      action='store_true',
                      dest='nocompress',
                      default=False,
                      help="Don't compress the ZODB backups.")

    parser.add_option('-B', '--keep-backups-count',
                      action='store',
                      dest='backups_keep_count',
                      type='int',
                      metavar='NUMBER',
                      default=DEFAULT_ZODB_BACKUPS_KEEP_COUNT,
                      help="The NUMBER of ZODB backups to keep. "
                      "The default is %s." % DEFAULT_ZODB_BACKUPS_KEEP_COUNT)

    parser.add_option('-s', '--send-notifications',
                      action='store',
                      dest='notifications',
                      type='choice',
                      metavar='FREQ',
                      choices=['daily','weekly', 'monthly'],
                      default=DEFAULT_NOTIFICATION_FREQ,
                      help="Send email notifications of frequence FREQ of "
                      "[daily|weekly|monthly]. Defaults to %s." %
                      str(DEFAULT_NOTIFICATION_FREQ))

def log(message, force=False, increment=0):
    """Log the given message to stderr.
    """
    message =  '    ' * increment + message
    if force or verbose:
        print >> sys.stderr, message

def pack(portal, days=0):
    db_id = portal._p_jar._db.database_name
    logger = logging.getLogger('')
    db = app.Control_Panel.Database[db_id]
    logger.info("Starting pack for %s, database name is '%s'", portal, db_id)
    db.manage_pack(days=days)
    logger.info("Pack of database '%s' done", db_id)

def backupZodb(zodb_path, backupdir_path, compress=True, backups_keep_count=0):
    """TODO : backupZodb should WARN and not perform this action if there isn't
    enough space left on target device. But unfortunately this requires parsing
    of platform specific information and there isn't any native python-way to
    do this yet.
    GR: taken from old cpshousekeeping.
    Obviously, this applies to FSStorage only.
    """
    log("\nChecking for backups ...")
    time_string = strftime(TIME_FORMAT, gmtime())
    file_name = '%s-%s' % (time_string, os.path.basename(zodb_path))
    zodb_backup_path = os.path.join(backupdir_path, file_name)
    command = "cp -p %s %s" % (zodb_path, zodb_backup_path)
    log("command = %s" % command, increment=1)
    os.system(command)
    if compress:
        compressFile(zodb_backup_path)

    if backups_keep_count > 0:
        log("Checking for potential backups to remove, "
            "keeping only the %s ones ..." % backups_keep_count, increment=1)
        file_names = os.listdir(backupdir_path)
        file_names = [x for x in file_names
                      if ZODB_BACKUP_FILENAME_REGEXP.match(x)]
        file_names.sort()
        file_names_to_delete = file_names[:-backups_keep_count]
        for file_name in file_names_to_delete:
            file_path = os.path.join(backupdir_path, file_name)
            log("Removing = %s ..." % file_path, increment=1)
            os.remove(file_path)
    log("Successful backup of the ZODB")


def exec_args():
    setup_optparser()
    portal, options, _ = cpsjob.bootstrap(app)
    portal_str = str(portal)

    global verbose
    verbose = options.verbose

    repotool = portal.portal_repository
    membtool = portal.portal_membership

    if options.purge_repository:
        log("\nPurging the document repository of %s ..." % portal_str)
        repotool.purgeDeletedRevisions()
        transaction.commit()
        log("Successfully purged repository of %s" % portal_str)

    if options.purge_localroles or options.purge_localroles_force:
        log("\nPurging the local roles of portal %s ..." % portal_str)
        mids = membtool.purgeDeletedMembersLocalRoles(
            lazy=not options.purge_localroles_force)
        transaction.commit()
        log(("Successfully purged localroles of %s " +
            "(found %d deleted members)") % (portal_str, len(mids)))
        if verbose and mids:
            log("Deleted members were:\n%s" % '\n'.join(mids))

    if options.purge_archived_revisions:
        keep_max = options.archived_revisions
        log("\nPurging archived revisions of documents of %s "
            "(keeping no more than %s archives per doc) ..."
            % (portal_str, keep_max))
        repotool.purgeArchivedRevisions(keep_max=keep_max)
        transaction.commit()
        log("Successfully purged archived revisions of " + portal_str)

    if options.notifications:
        freq = options.notifications
        log("\nSending %s notifications of %s ..." % (freq, portal_str))
        url = SEND_NOTIFICATIONS_PATTERN % (options.host_name,
                                            options.host_port,
                                            options.instance_id,
                                            options.notifications)
        try:
            meth = portal.cps_subscriptions_schedule_notifications
        except AttributeError:
            log("\nCPSSubscriptions does not seem to be active in %s",
                portal_str)
        else:
            meth(options.notifications)
            transaction.commit()
            log("Successfully sent notifications for %s" % portal_str)

    if options.pack_zodb:
        pack(portal, days=options.days)

    if options.backup:
        backupZodb(options.zodbfile_path, options.backupdir_path,
                   not options.nocompress, options.backups_keep_count)


# Shell conversion
if __name__ == '__main__':
    exec_args()
