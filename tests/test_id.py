# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# (C) Copyright 2010 AFUL <http://aful.org>
# Authors:
# M.-A. Darche <madarche@nuxeo.com>
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

import unittest

from OFS.Folder import Folder
from Acquisition import aq_inner, aq_parent

from Products.CPSUtil.id import generatePassword, generateId, generateFileName

class FakeUrlTool(Folder):

    def __init__(self):
        Folder.__init__(self, 'portal_url')

    def getPortalObject(self):
        return self.aq_inner.aq_parent


class Test(unittest.TestCase):

    def testPassword(self):
        password = generatePassword(min_chars=20, max_chars=30)
        password_length = len(password)
        self.assert_(password_length >= 20 and password_length <= 30)

    def testGenerateIdBasic(self):
        # stupid id should return random number
        for id in ('', '-', ' ', '.'):
            self.assert_(len(generateId(id)) > 0, id)

        # Testing that the generated strings are free of special characters and
        # lower case.
        s1 = u"C'est l'\xe9t\xe9 !"
        self.assertEquals(generateId(s1), "c-est-l-ete")
        self.assertEquals(generateId(s1, lower=True), "c-est-l-ete")
        self.assertEquals(generateId(s1, lower=False), "C-est-l-ete")

        s2 = u"C'est !!! l'\xe9t\xe9 !!!!"
        self.assertEquals(generateId(s2), "c-est-l-ete")
        self.assertEquals(generateId(s2, lower=True), "c-est-l-ete")
        self.assertEquals(generateId(s2, lower=False), "C-est-l-ete")

        # Testing the max_chars parameter
        s3 = "On rails CPS is for a loooooooooooooooooooooooooooong time"
        # With max_chars = 0 the length of the generated ID should be the same
        # than this of the input.
        max_chars = 0
        self.assertEquals(generateId(s3, max_chars=max_chars, lower=False),
                          s3.replace(' ', '-'))
        self.assertEquals(len(generateId(s3, max_chars=max_chars, lower=False)),
                          len(s3))
        # With max_chars > 0 the length of the generated ID should be lower or
        # equal to max_chars.
        max_chars = 24
        self.assert_(len(generateId(s3)) <= max_chars)

        # Testing the word_separator parameter
        self.assertEquals(generateId(s2, lower=False, word_separator='-'), "C-est-l-ete")
        self.assertEquals(generateId(s2, lower=False, word_separator='_'), "C_est_l_ete")
        self.assertEquals(generateId(s2, lower=True, word_separator='-'),
                          "c-est-l-ete")
        self.assertEquals(generateId(s2, lower=True, word_separator='_'),
                          "c_est_l_ete")


    def testGenerateIdMeaninglessWordsRemoval(self):
        # Testing that meaningless words are removed
        s1 = "This is a message from the president"
        meaningless_words_en = "a the this these those of am is are has have or and i maybe perhaps"
        self.assertEquals(generateId(s1, lower=True,
                                     meaningless_words=meaningless_words_en),
                          "message-from-president")

        s2 = u"Voil\xe0 l'\xe9t\xe9"
        meaningless_words_fr = "et ou un une le la les l de des ces que qui est sont a ont je voici"
        self.assertEquals(generateId(s2, lower=True,
                                     meaningless_words=meaningless_words_fr),
                          "voila-ete")

        # Should keep meaningless word if their is only one
        for id in ('a', 'the'):
            self.assertEquals(generateId(id, meaningless_words=meaningless_words_en), id)

        # Should keep something if the title is meaningless
        self.assertEquals(generateId("the the", meaningless_words=meaningless_words_en),
                          "the-the")


    def testGenerateIdDeterminism(self):
        # Test if the generateId() method always return the same id when there
        # isn't any container in which objects are created.
        #
        # Of course if an Id already exists in a given container, the generateId()
        # method does NOT return the same value, since its purpose is to generate
        # unique and meaningful Ids in a given container.

        examples = ["We are belong to us",
                    u"C'est l'\xe9t\xe9 !",
                    # This kind of string can be found on wiki links
                    "?Mine",
                    "???",
                    "???????????",
                   ]
        for s in examples:
            res1 = generateId(s, container=None)
            res2 = generateId(s, container=None)
            self.assertEquals(res1, res2, "Results differ for string '%s'" % s)


    def testGenerateIdUnicity(self):
        # unicity is tested under a context
        portal = Folder('portal')
        portal._setObject('portal_url', FakeUrlTool())
        portal._setObject('index_html', Folder('index_html'))
        portal._setObject('folder', Folder('folder'))
        folder = portal.folder

        # acceptable id
        res1 = generateId('content', container=folder)
        folder._setObject(res1, Folder(res1))
        res2 = generateId('content', container=folder)
        self.assertNotEquals(res1, res2, "id generated already exists: " + res1)

        # special ids
        # index_html is accepted
        self.assertEquals(generateId('index_html', container=folder),
                          'index_html')
        # portal_url is not accepted (prevent acquisition related problems)
        self.assertNotEquals(generateId('portal_url', container=folder),
                             'portal_url')


    def testGenerateIdEmpty(self):
        # These are random, so they should differ.
        res1 = generateId('', container=None)
        res2 = generateId('', container=None)
        self.assertNotEquals(res1, res2)

    def testSomeExamples(self):
        mapping = {
            'Le ciel est bleu': 'Le-ciel-est-bleu',
            'Le ciel est bleu ': 'Le-ciel-est-bleu',
            ' Le ciel est bleu ': 'Le-ciel-est-bleu',
            'open+source': 'open-source',
            'open + source': 'open-source',
            'open  + source': 'open-source',
            'S. Fermigier first law of project management':
                'S-Fermigier-first-law-of',
        }
        for key, value in mapping.items():
            self.assertEquals(generateId(key, lower=False), value)


    def testKeepId_01(self):
        # we want to keep valid id, like user_id in personal members area
        my_id = 'my_id_01'
        self.assertEquals(generateId(my_id), my_id)

    def testKeepId_02(self):
        my_id = 'my-id_01'
        self.assertEquals(generateId(my_id), my_id)

    def testGenerateFileName(self):
       self.assertEquals(generateFileName("My Document.doc"), 'My_Document.doc')
       self.assertEquals(generateFileName("MyDocument.sxw"), 'MyDocument.sxw')
       self.assertEquals(generateFileName(u"Proc\xe9dures finales.sxw"),
                         'Procedures_finales.sxw')


       # check removing of special leading and trailing characters
       # currently special leading are: '_' and '.'
       # special trailing is '_'
       self.assertEquals(generateFileName('...___....file.zip__'), 'file.zip')

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
