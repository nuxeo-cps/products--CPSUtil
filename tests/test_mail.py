# (C) Copyright 2010 Georges Racinet
# Author: Georges Racinet <georges@racinet.fr>
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
from Testing.ZopeTestCase import doctest

from Products.CPSUtil.mail import send_mail

class FakeMailHost:

  def _send(self, envelope_from, envelope_to, msg):
      """Reproduce here what the true mailhost and/or smtp servers refuse.

      Preliminary notes:
        unicode strings in envelope_to as in current tests are ok. Resulting
        mail has only the "core" email adress in its envelope-to header.
        This is the doing of either smtplib or the testing MTA (Exim 4.63)
      """
      pass

class MailTest(unittest.TestCase):

    def setUp(self):
        self.MailHost = FakeMailHost()
        self.default_charset = 'utf-8'

    def test_unicode_to(self):
        send_mail(self, u'gr <gr@example.com>', 'CPS Portal <cps@example.com>',
                  'The subject', 'The body')

        send_mail(self, u'gr\xe9 <gr@example.com>',
                  'CPS Portal <cps@example.com>',
                  'The subject', 'The body')

    def test_subject_unicode(self):
        # was an error occuring with preamble, for multiparts only
        send_mail(self, '<gr@example.com', 'cps@example.com',
                  u'Cr\xe9ation de contenu', '<html><body>Body</body></html>',
                  plain_text=False, encoding='utf-8')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MailTest))
    suite.addTest(doctest.DocTestSuite('Products.CPSUtil.mail'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
