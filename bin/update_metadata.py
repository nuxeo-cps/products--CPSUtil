#!/usr/bin/python
#
# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Olivier Grisel <og@nuxeo.com>
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
"""A script to generate or update .metadata files for file in skins directories

This is useful to associate image files to some HTTPCacheManager.

For usage info and options, type:

  $ python update_metadata.py --help
"""

import os
from optparse import OptionParser
from ConfigParser import ConfigParser, NoOptionError, NoSectionError

# Default values that can be overridden by command lines options
DEFAULT_CACHE_ID = 'cps_default_http_cache'
DEFAULT_SUFFIXES = ('gif', 'png', 'jpeg', 'jpg', 'css', 'js')
DEFAULT_IGNORE_SUBDIRS = ('.svn', 'CVS')

def execArgs():
    """Analyze command line arguments.
    """
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option('-c', '--cache-id',
                      action='store',
                      dest='cache_id',
                      default=DEFAULT_CACHE_ID,
                      help="Id of the HTTP Cache Manager.")

    (options, args) = parser.parse_args()


    for root, dirs, files in os.walk('.'):
        # Updating or generating metadata files
        for filename in files:
            if filename.split('.')[-1] in DEFAULT_SUFFIXES:
                metadata_file = filename + '.metadata'
                metadata_file_path = os.path.join(root, metadata_file)
                data = {}
                if metadata_file in files:
                    data = loadConfigurationFile(metadata_file_path)
                data.setdefault('cache', options.cache_id)
                print "Updating %s ..." % metadata_file_path,
                new_file = file(metadata_file_path, 'w')
                new_file.write('[default]\n')
                for key, value in data.items():
                    new_file.write("%s=%s\n" % (str(key), str(value)))
                new_file.close()
                print 'done'

        # Ignoring some subdirs
        for ignore in DEFAULT_IGNORE_SUBDIRS:
            if ignore in dirs:
                dirs.remove(ignore)


def loadConfigurationFile(filename, section='default', default={}):
    """Parse existing .metadata file and return content as a dictionary
    """
    try:
        fh = file(filename, 'r')
    except IOError:
        print "Error opening %s" % filename
        return default
    parser = ConfigParser()
    parser.readfp(fh)
    fh.close()
    try:
        options = parser.options(section)
    except NoSectionError:
        print ("Error file %s don't have [%s] section" % (filename, section))
        return default
    kw = {}
    for option in options:
        kw[option] = parser.get(section, option)
    return kw


# Shell conversion
if __name__ == '__main__':
    execArgs()

