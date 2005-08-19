# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Authors:
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
import unittest
from Products.CPSUtil.id import generatePassword, generateId

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
        s1 = "C'est l'été !"
        self.assertEquals(generateId(s1), "C-est-l-ete")
        self.assertEquals(generateId(s1, lower=True), "c-est-l-ete")

        s2 = "C'est !!! l'été !!!!"
        self.assertEquals(generateId(s2), "C-est-l-ete")
        self.assertEquals(generateId(s2, lower=True), "c-est-l-ete")

        # Testing the max_chars parameter
        s3 = "On rails CPS is for a loooooooooooooooooooooooooooong time"
        # With max_chars = 0 the length of the generated ID should be the same
        # than this of the input.
        max_chars = 0
        self.assertEquals(generateId(s3, max_chars=max_chars),
                          s3.replace(' ', '-'))
        self.assertEquals(len(generateId(s3, max_chars=max_chars)),
                          len(s3))
        # With max_chars > 0 the length of the generated ID should be lower or
        # equal to max_chars.
        max_chars = 24
        self.assert_(len(generateId(s3)) <= max_chars)

        # Testing the word_separator parameter
        self.assertEquals(generateId(s2, word_separator='-'), "C-est-l-ete")
        self.assertEquals(generateId(s2, word_separator='_'), "C_est_l_ete")
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

        s2 = "Voilà l'été"
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
                    "C'est l'été !",
                    # This kind of string can be found on wiki links
                    "?Mine",
                    "???",
                    "???????????",
                   ]
        for s in examples:
            res1 = generateId(s, container=None)
            res2 = generateId(s, container=None)
            self.assertEquals(res1, res2, "Results differ for string '%s'" % s)


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
            self.assertEquals(generateId(key), value)


    def testNonRegression1(self):
        title = 'S. Fermigier first law of project management'
        id = generateId(title)
        self.assertEquals(id, 'S-Fermigier-first-law-of')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
