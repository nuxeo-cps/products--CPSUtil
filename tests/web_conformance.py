# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# M.-A. Darche
# Stefane Fermigier <sf@nuxeo.com>
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
"""A module which provides unit test methods for web standards conformance.

The tested web standards are XML, XHTML, HTML and CSS.

The code in this module relies on many packages and executables present on the
host Unix system.

The XML, XHTML and HTML validation methods rely on the following packages that
need to be installed (the package names are for a Debian-based system):
xml-core xmllint w3c-dtd-xhtml sgml-base sgml-data

Without the packages containing the different standard schemas (DTD, etc.), that
is w3c-dtd-xhtml sgml-base sgml-data, it is not possible to use xmllint with the
"--no-net" option since xmllint will need to fetch the schemas over the network by
itself instead of fetching them in the local XML and SGML catalogs.

The CSS validation methods rely on an installed JVM and the JAR of the
W3C CSS validator present at this precise location:
/usr/local/share/java/css-validator.jar

A binary distribution of the W3C CSS validator (css-validator.jar) can be found
at http://www.illumit.com/css-validator/ or build with Ant from
http://dev.w3.org/cvsweb/2002/css-validator/
"""

import os
import re
import tempfile
import popen2

CSS_VALIDATOR_JAR_PATH = '/usr/local/share/java/css-validator.jar'

#
# TODO: duplication -> refactor
#
def assertWellFormedXml(xml, page_id=None):
    fd, file_path = tempfile.mkstemp()
    f = os.fdopen(fd, 'wc')
    f.write(xml)
    f.close()
    cmd = "xmllint --noout %s" % file_path
    stdout, stdin, stderr = popen2.popen3(cmd)
    result = stderr.read()
    if not result.strip() == '':
        if page_id:
            raise AssertionError("%s is not well-formed XML:\n\n%s"
                % (page_id, result))
        else:
            raise AssertionError("not well-formed XML:\n\n%s" % result)
    os.remove(file_path)

def isWellFormedXml(xml):
    fd, file_path = tempfile.mkstemp()
    f = os.fdopen(fd, 'wc')
    f.write(xml)
    f.close()
    status = os.system("xmllint --noout %s" % file_path)
    os.remove(file_path)
    return status == 0

def assertValidHtml(html, page_id=None):
    fd, file_path = tempfile.mkstemp()
    f = os.fdopen(fd, 'wc')
    f.write(html)
    f.close()
    cmd = "xmllint --valid --html --nonet --noout %s" % file_path
    stdout, stdin, stderr = popen2.popen3(cmd)
    result = stderr.read()
    if not result.strip() == '':
        if page_id:
            raise AssertionError("%s is not valid HTML:\n%s"
                % (page_id, result))
        else:
            raise AssertionError("Invalid HTML:\n%s" % result)
    os.remove(file_path)

def assertValidXhtml(html, page_id=None):
    fd, file_path = tempfile.mkstemp()
    f = os.fdopen(fd, 'wc')
    f.write(html)
    f.close()
    cmd = "xmllint --valid --nonet --noout %s" % file_path
    stdout, stdin, stderr = popen2.popen3(cmd)
    result = stderr.read()
    if not result.strip() == '':
        if page_id:
            raise AssertionError("%s is not valid XHTML:\n%s"
                % (page_id, result))
        else:
            raise AssertionError("Invalid XHTML:\n%s" % result)
    os.remove(file_path)

# DOTALL: Make the "." special character match any character at all,
# including a newline; without this flag, "." will match anything except a
# newline.
#
# For example:
#
# <div id="errors">
# rrrrrrrRRRRRR
# </div>
# <div id="warnings">
# Hummmmmmmmmmm
# </div>
# <div id="css">
# </div>
#
# makes it possible to retrieve both
# "rrrrrrrRRRRRR" and "Hummmmmmmmmmm"
#
CSS_VALIDATOR_ERRORS_REGEXP = re.compile(
    u'<div id="errors">(.*)</div>.*?<div id="warnings">(.*)</div>.*?<div id="css">',
    re.DOTALL)

def assertValidCss(css, ressource_name='', css_profile='css21',
                   input_format='css',
                   fail_on_warnings=False):
    """Check if <css> is valid CSS using the W3C CSS validator.
    """
    is_valid, errors = isValidCss(css, css_profile, input_format,
                                  fail_on_warnings)
    if not is_valid:
        raise AssertionError("%s is or contains invalid CSS:\n%s"
                             % (ressource_name, errors))

def isValidCss(css, css_profile='css21',
               input_format='css',
               fail_on_warnings=False):
    """Check if <css> is valid CSS using the W3C CSS validator and return
    the errors found if any.

    input_format can be either "css", "html" or "xml".

    The test is done using a local css validator if one is present.
    """
    is_valid = True
    errors = ""
    # Version using the online W3C CSS validator.
    # Using the online W3C CSS validator should be avoided since it may be
    # off-line for maintainance or refusing too close connexions to avoid
    # DOS situations.
    #import urllib2, urllib
    #CHECKER_URL = 'http://jigsaw.w3.org/css-validator/validator'
    #data = urllib.urlencode({
    #    'text': css,
    #    'warning': '1',
    #    'profile': css_profile,
    #    'usermedium': 'all',
    #})
    #url = urllib2.urlopen(CHECKER_URL + '?' + data)
    #result = url.read()

    try:
        java_binary_path = _getBinaryPath('java')
    except Exception, exception:
        print "isValidCSS: %s" % str(exception)
        return is_valid, errors
    # It is required that the file passed to the validator has a file
    # suffix corresponding to its content type since the command line
    # interface of the validator uses this to decide how to process the
    # file.
    suffix = '.' + input_format
    fd, file_path = tempfile.mkstemp(suffix)
    f = os.fdopen(fd, 'wc')
    f.write(css)
    f.close()
    if not os.access(CSS_VALIDATOR_JAR_PATH, os.R_OK):
        print ("isValidCSS: %s not present or not readable "
               "=> no CSS validation occured" % css_validator_jar_path)
        return is_valid, errors
    cmd = ('%s -jar %s -html -%s %s'
           % (java_binary_path, CSS_VALIDATOR_JAR_PATH,
              css_profile, file_path))
    stdout, stdin, stderr = popen2.popen3(cmd)
    result = stdout.read()
    os.remove(file_path)
    match = CSS_VALIDATOR_ERRORS_REGEXP.search(result)
    is_valid = not match
    if not is_valid:
        errors = match.group(1)
    return is_valid, errors

class MissingBinary(Exception): pass

def _getBinaryPath(binary_name):
    """Return the path for the given binary if it can be found and if it is
    executable.
    """
    binary_search_path = os.environ['PATH'].split(os.pathsep)
    binary_path = None
    mode = os.R_OK | os.X_OK
    for p in binary_search_path:
        path = os.path.join(p, binary_name)
        if os.access(path, mode):
            binary_path = path
            break
    else:
        raise MissingBinary('Unable to find binary "%s"' % binary_name)
    return binary_path


