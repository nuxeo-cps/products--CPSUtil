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

import os
import re
import gzip
from time import strftime, gmtime
import logging
logger = logging.getLogger("housekeeping")

import transaction
from ZODB.FileStorage.FileStorage import FileStorage
from ZEO.ClientStorage import ClientStorage

from Products.CPSUtil import cpsjob

DEFAULT_ARCHIVED_REVISION_COUNT = 0
DEFAULT_HISTORY_DAYS = 0
DEFAULT_ZODB_BACKUP_DIR_PATH = '/var/backups/zodb'
DEFAULT_ZODB_BACKUPS_KEEP_COUNT = 7
DEFAULT_NOTIFICATION_FREQ = None

TIME_FORMAT = '%Y-%m-%d_%H:%M'
# This regexp matches file names of the form
# YYYY-MM-dd_hh:mm-xxxxxxxxxx
# Examples:
# 2007-09-17_11:24-Data.fs
# 2007-09-17_11:24-Data.fs.gz
ZODB_BACKUP_FILENAME_REGEXP = re.compile(r'\d+-\d{2}-\d{2}_\d{2}:\d{2}-.+')
SEND_NOTIFICATIONS_PATTERN = 'http://%s:%s/%s/cps_subscriptions_schedule_notifications?subscription_mode=%s'


def setup_optparser(parser=cpsjob.optparser):
    usage = """Usage: %prog [options] <portal id>

Example:
%prog --verbose --user admin --purge-repository --purge-localroles-force --pack-zodb --backupdir /var/backups/zodb/www.mysite.net cps
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

    parser.add_option('-b', '--backup',
                      action='store_true',
                      dest='backup',
                      default=False,
                      help="Backup the ZODB that has just been packed "
                      """using the "cp" command (FileStorage or ZEO only).
                      Autodetects the file to backup.""")

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

def getHumanReadableSize(octet_size):
    """Returns a string that is a human readable file size.
    """
    mega = 1024*1024
    kilo = 1024

    if octet_size is None or octet_size <= 0:
        return "0"
    elif octet_size >= mega:
        if octet_size == mega:
            return "1M"
        else:
            msize = float(octet_size/float(mega))
            msize = float('%.02f' % msize)
            return "%sM" % msize
    elif octet_size >= kilo:

        if octet_size == kilo:
            return "1K"
        else:
            ksize = float(octet_size/float(kilo))
            ksize = float('%.02f' % ksize)
            return "%sK" % ksize
    else:
        return str(octet_size)

def getHumanReadableFileSize(path):
    """Return a hr representation of the file size, or 'unknown'."""
    if (path is None or not os.path.isfile(path)
        or not os.access(path, os.R_OK)):
        return 'unknown'
    return getHumanReadableSize(os.path.getsize(path))

def getZodb(portal):
    return portal._p_jar._db

def getDbFilePath(portal=None, db=None):
    """Return the path to DB file, if applicable, or None."""

    if db is None:
        if portal is None:
            raise ValueError("portal and db both None")
        db = getZodb(portal)

    db_id = db.database_name
    storage = db._storage
    if isinstance(storage, FileStorage):
        path = storage._file_name
        logger.info("Database %s uses FileStorage at %s", db_id, path)
        return path
    elif isinstance(storage, ClientStorage):
        path = storage._server.get_info()['name']
        logger.info("Database %s is a ZEO mount for a FileStorage at %s",
                    db_id, path)
        return path

def pack(portal, days=0):
    db = getZodb(portal)
    db_id = db.database_name
    db_ctl = app.Control_Panel.Database[db_id]
    db_path = getDbFilePath(db=db)

    logger.warn("Starting pack for %s, database name is '%s' (size %s)",
                portal, db_id, getHumanReadableFileSize(db_path))
    db_ctl.manage_pack(days=days)
    logger.warn("Pack of database '%s' done. Current size %s", db_id,
                getHumanReadableFileSize(db_path))

def backupZodb(portal, backupdir_path, compress=True, backups_keep_count=0):
    """TODO : backupZodb should WARN and not perform this action if there isn't
    enough space left on target device. But unfortunately this requires parsing
    of platform specific information and there isn't any native python-way to
    do this yet.
    GR: taken from old cpshousekeeping and refactored a bit to take advantage
    from internal knowledge of ZODB
    """
    db = getZodb(portal)
    db_id = db.database_name
    zodb_path = getDbFilePath(db=db)

    if zodb_path is None:
        logger.error("Database '%s' (for %s) is neither FileStorage nor ZEO "
                     " based. Use other means to perform the backup",
                     db_id, portal)
        return

    if not os.path.isfile(zodb_path) or not os.access(zodb_path, os.R_OK):
        logger.error("The ZEO mounted database '%s' (for %s) does not "
                     "seem to be a FileStorage available from this "
                     "script. Name found is '%s'. If this does not look "
                     "like a path on the ZEO Server host, you are not on "
                     "FileStorage. Otherwise, check permissions and "
                     "overall availability from this host.",
                     db_id, portal, zodb_path)
        return


    time_string = strftime(TIME_FORMAT, gmtime())
    file_name = '%s-%s' % (time_string, os.path.basename(zodb_path))
    zodb_backup_path = os.path.join(backupdir_path, file_name)
    command = "cp -p %s %s" % (zodb_path, zodb_backup_path)

    if backups_keep_count > 0:
        logger.warn("Checking for potential backups to remove, "
                    "keeping only the %d latest ones ...", backups_keep_count)
        file_names = os.listdir(backupdir_path)
        file_names = [x for x in file_names
                      if ZODB_BACKUP_FILENAME_REGEXP.match(x)]
        file_names.sort()
        file_names_to_delete = file_names[:-backups_keep_count]
        for file_name in file_names_to_delete:
            file_path = os.path.join(backupdir_path, file_name)
            logger.info("Removing %s ..." % file_path)
            os.remove(file_path)

    logger.info("backup command = %s" % command)
    os.system(command)
    if compress:
        compressFile(zodb_backup_path)

    logger.warn("Successful backup of the ZODB")

def compressFile(file_path):
    """Compress a file using GZIP.
    """
    logger.info("Compressing %s ...", file_path)
    f_in = open(file_path, 'rb')
    gzip_file_path = file_path + '.gz'
    f_out = gzip.open(gzip_file_path, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    os.remove(file_path)
    logger.info("Compressing done : %s", gzip_file_path)

def exec_args():
    setup_optparser()
    portal, options, _ = cpsjob.bootstrap(app)
    portal_str = str(portal)

    repotool = portal.portal_repository
    membtool = portal.portal_membership

    if options.purge_repository:
        logger.warn("Purging the document repository of %s ...", portal_str)
        repotool.purgeDeletedRevisions()
        transaction.commit()
        logger.warn("Successfully purged repository of %s", portal_str)

    if options.purge_localroles or options.purge_localroles_force:
        logger.warn("Purging the local roles of portal %s ...", portal_str)
        mids = membtool.purgeDeletedMembersLocalRoles(
            lazy=not options.purge_localroles_force)
        transaction.commit()
        logger.warn(
            "Successfully purged localroles of %s (found %d deleted members)",
            portal_str, len(mids))
        logger.info("Deleted members were:\n%s", '\n'.join(mids))

    if options.purge_archived_revisions:
        keep_max = options.archived_revisions
        logger.warn("Purging archived revisions of documents of %s "
            "(keeping no more than %s archives per doc) ...",
                     portal_str, keep_max)
        repotool.purgeArchivedRevisions(keep_max=keep_max)
        transaction.commit()
        logger.warn("Successfully purged archived revisions of %s", portal_str)

    if options.notifications:
        freq = options.notifications
        logger.warn("Sending %s notifications of %s ...", freq, portal_str)
        url = SEND_NOTIFICATIONS_PATTERN % (options.host_name,
                                            options.host_port,
                                            options.instance_id,
                                            options.notifications)
        try:
            meth = portal.cps_subscriptions_schedule_notifications
        except AttributeError:
            logger.error("CPSSubscriptions does not seem to be active in %s",
                portal_str)
        else:
            meth(options.notifications)
            transaction.commit()
            logger.warn("Successfully sent notifications for %s", portal_str)

    if options.pack_zodb:
        pack(portal, days=options.days)

    if options.backup:
        backupZodb(portal, options.backupdir_path,
                   not options.nocompress, options.backups_keep_count)


# Shell conversion
if __name__ == '__main__':
    exec_args()
