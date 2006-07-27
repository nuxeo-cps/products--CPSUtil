# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# - Anahide Tchertchian <at@nuxeo.com>
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
"""Helper for running tests using a testing environment
"""

from App.config import getConfiguration

def setTestingEnvironmentIfNeeded():
    """Set a test environment if needed

    This should be called in the __init__.py file of modules that are imported
    by the test runner when looking for tests.

    If import is not done by the test runner, testing environment will not be
    set.
    """
    from inspect import currentframe
    # frame number used is 3 because:
    # - first frame is current environment.py file
    # - second frame is the product __init__.py file
    # - third frame is the testrunner.py file
    filename = currentframe(3).f_code.co_filename
    if '/ZopeTestCase/' in filename or filename.endswith("/testrunner.py"):
        getConfiguration().testing = True
    del filename, currentframe


def isTestingEnvironment():
    """Test if we're in a test environment
    """
    config = getConfiguration()
    testing = getattr(config, 'testing', False)
    return testing
