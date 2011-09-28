# -*- coding: iso-8859-15 -*-
# (C) Copyright 2003-2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
# Stefane Fermigier <sf@nuxeo.com>
# Tarek Ziade <tziade@nuxeo.com>
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
"""Utility functions for generating and manipulating IDs, logins and passwords.
"""

import re
import random
import md5
import string
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, INFO, DEBUG

from text import toAscii

# This string contain non-misleading characters that can safely be read and used
# by users. Misleading characters include for example the "l" letter that can be
# mistaken as the "1" number, without the "0" number that can be mistaken as the
# "O" letter, etc.
SAFE_CHARS_FOR_PASSWORD = "-abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ123456789"

# Allowing this method to be imported in restricted code
ModuleSecurityInfo('Products.CPSUtil.id').declarePublic('generatePassword')
def generatePassword(min_chars=10, max_chars=20):
    """Generate a readable password.

    Generate a readable password, ie without misleading characters such as the
    "l" letter that can be mistaken as the "1" number, without the "0" number
    that can be mistaken as the "O" letter, etc."""
    password = ""
    password_size = random.randint(min_chars, max_chars)
    for i in range(password_size):
        password += random.choice(SAFE_CHARS_FOR_PASSWORD)
    return password


# A regexp that does word splitting using alpha-numerical words.
# Note that we include the "_" character here so that no word splitting is done
# through this character. This is a compatibility issue with previous versions
# of CPS that were using "_" as a word separator.
WORD_SPLITTING_REGEXP = re.compile('[^_a-zA-Z0-9]*')

# Allowing this method to be imported in restricted code
ModuleSecurityInfo('Products.CPSUtil.id').declarePublic('generateId')
def generateId(s, max_chars=24, lower=True, word_separator='-',
               portal_type=None, meaningless_words=[], container=None):
    """Generate an id from a given string.

    This method avoids collisions and prevents words' cut.

    The optional max_chars parameter truncates the generated ID if set to a
    strictly positive number.

    The optional lower parameter sets to lower-case the generated ID.

    The optional word_separator parameter is the separator that will be inserted
    between words that compose the generated ID. This separator will be present
    in the URLs of portal objects and documents.

    The optional portal_type parameter is not used at this time, but might be
    interesting to generate IDs in special manners for certain portal_types.

    The optional meaningless_words parameter removes all the specified words
    from the generated ID. The words are compared in a case sensitive manner.

    The optional container parameter is used to check if the generated ID is not
    already used in the specified container or does not correspond to a reserved
    word in this container.

    This method is to be used for Latin-9 encoded strings.
    """
    # TODO: similar code is still duplicated in other places like
    # CPSForum/skins/forum_default/forum_create.py
    # CPSWebMail/Attachment.py

    if not s:
        # Generate a random id
        s = ''.join([random.choice(string.letters) for i in range(8)])

    id = toAscii(s)
    if lower:
        id = id.lower()

    # Performing word splitting on the id.
    # This is done because this method prevents words' cut.
    words = WORD_SPLITTING_REGEXP.split(id)
    words = [w for w in words if w]

    # Removing meaningless words if this has been asked
    if meaningless_words:
        # Removing meaningless words and obtaining a cleaned words list, but
        # making sure though that we at least have one word left.
        words_cleaned = [w for w in words if w not in meaningless_words]
        if len(words_cleaned):
            words = words_cleaned

    if not words:
        hash_object = md5.new()
        hash_object.update(id)
        id = generateId(hash_object.digest())
    # Doing the truncation if max_chars has been specified
    elif max_chars > 0:
        # Preventing word cuts if a max_chars truncation has been asked
        id = words[0] # The id needs to contain at least one word
        words = words[1:]
        while words and ((len(id) + len(words[0]) + 1) <= max_chars):
            id += word_separator + words[0]
            words = words[1:]
        id = id[:max_chars]
    else:
        id = word_separator.join(words)

    if container is not None:
        # Ensuring that the id is not a portal reserved id (this is a case where
        # acquisition is a pain) and that the id is not used in the given
        # container.
        # "index_html", "sections" and "workspaces" should always be usable.
        portal = getToolByName(container, 'portal_url').getPortalObject()
        # It's needed to allow index_html for join code
        while ((portal.hasObject(id)
                and id not in ('index_html', 'sections', 'workspaces'))
               or container.hasObject(id)):
            # The id is reserved we need to compute another id
            id = _generateAnotherId(id)

    return id


GENERATION_MAX_TRIES = 500

def _generateAnotherId(id):
    """Generate another ID from the given one.

    This is to be used to avoid collisions.
    """
    m = re.match('(.*)\d\d\d\d$', id)
    if m is not None:
        prefix = m.group(1)
    else:
        prefix = id

    tries = 0
    while 1:
        tries += 1
        if tries == GENERATION_MAX_TRIES:
            # grow prefix
            prefix = id
            tries = 0
        suffix = str(random.randrange(1000, 10000))
        id = prefix + suffix
        return id


SAFE_CHARS_FOR_FILE_NANME = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_.'

def generateFileName(name, context=None):
    """Generate a safe file name (without any special characters) from the
    given name.
    """
    name = toAscii(name, context=None)
    translation_table = string.maketrans(r"'\;/ &:",
                                         r"_______")
    name = name.translate(translation_table)
    name = ''.join([c for c in name if c in SAFE_CHARS_FOR_FILE_NANME])
    name = name.lstrip('_.').rstrip('_')

    return name
