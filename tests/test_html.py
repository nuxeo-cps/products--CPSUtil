# -*- coding: iso-8859-15 -*-
# (C) Copyright 2005-2006 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Tarek Ziadé <tz@nuxeo.com>
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
from Products.CPSUtil.html import XhtmlSanitizer
from Products.CPSUtil.html import HTMLSanitizer
from Products.CPSUtil.html import sanitize
from Products.CPSUtil.html import getHtmlBody

class Test(unittest.TestCase):

    def testXhtmlSanitizing(self):
        res = sanitize('ftgyuhjik')
        self.assertEquals(res, 'ftgyuhjik')

        # Broken tags should not break the sanitizer.
        # A better sanitizer would sanitizes those broken tags instead of giving
        # up and returning the text uncleaned.
        res = sanitize('<!12345>')
        self.assertEquals(res, '<!12345>')
        res = sanitize('<foo@bar.org>')
        self.assertEquals(res, '<foo@bar.org>')
        res = sanitize('AAAAAAAA <foo@bar.org>BB')
        self.assertEquals(res, 'AAAAAAAA <foo@bar.org>BB')

        res = sanitize('<a>ftgyuhjik</a>')
        self.assertEquals(res, '<a>ftgyuhjik</a>')

        res = sanitize('AAA<br>BBB')
        self.assertEquals(res, 'AAA<br/>BBB')

        res = sanitize('<html>ftgyuhjik</html>')
        self.assertEquals(res, 'ftgyuhjik')

        res = sanitize('AAA<html>ftgyuhjik</html>BB')
        self.assertEquals(res, 'AAAftgyuhjikBB')

        res = sanitize('<html>ftg<strong>yuh</strong> jik</html>')
        self.assertEquals(res, 'ftg<strong>yuh</strong> jik')

        res = sanitize('<html>ftg<strong>yuh  </strong>jik</html>')
        self.assertEquals(res, 'ftg<strong>yuh  </strong>jik')

        res = sanitize('yu<script langage="javascript">h</script></c>')
        self.assertEquals(res, 'yuh')

        res = sanitize('dfrtgyhju<span class="myclass">ghj</span>')
        self.assertEquals(res, 'dfrtgyhju<span class="myclass">ghj</span>')

        res = sanitize('dfrtgyhju<span class="myclass" >ghj</span>')
        self.assertEquals(res, 'dfrtgyhju<span class="myclass">ghj</span>')

        res = sanitize('debian <div>fsf dfrtgyhju<span class="myclass" >ghj</span></di>')
        self.assertEquals(res, 'debian <div>fsf dfrtgyhju<span class="myclass">ghj</span></div>')

        res = sanitize('<a href="../../../../../../../view" accesskey="U" title="wii" _base_href="http://localhost:29980/cps2/sections/wii/we/">wii</a>')
        self.assertEquals(res, '<a href="../../../../../../../view" title="wii" _base_href="http://localhost:29980/cps2/sections/wii/we/">wii</a>')

        markup = '<address>Paris</address><blockquote><p>Paix longue</p></blockquote>'
        res = sanitize(markup)
        self.assertEquals(res, markup)

        markup = '<q>Paix courte</q><cite>22.3.4</cite><abbr>CNRS</abbr><acronym>LASER</acronym>'
        res = sanitize(markup)
        self.assertEquals(res, markup)

        # Testing tag replacements
        res = sanitize('ftg<b>yuh</b>jik abcde')
        self.assertEquals(res, 'ftg<strong>yuh</strong>jik abcde')

        res = sanitize('<span>ftg<b>yuh</b>jik abcde')
        self.assertEquals(res, '<span>ftg<strong>yuh</strong>jik abcde</span>')

        res = sanitize('<html>ftg<b>yuh</b>jik</html>')
        self.assertEquals(res, 'ftg<strong>yuh</strong>jik')

        res = sanitize('ftg<i>yuh</i>jik')
        self.assertEquals(res, 'ftg<em>yuh</em>jik')

        res = sanitize('ftg<i>yuh </i>jik')
        self.assertEquals(res, 'ftg<em>yuh </em>jik')

        res = sanitize('ftg<i>  yuh</i>jik')
        self.assertEquals(res, 'ftg<em>  yuh</em>jik')

        res = sanitize("<p>TITRE VI : DISPOSITIONS DIVERSES.<br /> Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.</p>",
                       tags_to_keep=[])
        self.assertEquals(res, "TITRE VI : DISPOSITIONS DIVERSES. Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.")
        # Testing entities
        inp = '&laquo;&agrave;&raquo'
        self.assertEquals(sanitize(inp), inp)

        # Testing support of XHTML notations such as <br/> and <hr/>
        res = sanitize("<p>TITRE VI :<hr/> DISPOSITIONS DIVERSES.<br/> Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.</p>",
                       tags_to_keep=[])
        self.assertEquals(res, "TITRE VI : DISPOSITIONS DIVERSES. Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.")
        res = sanitize("""<p>TITRE VI :<hr class="spacer"/> <hr/>DISPOSITIONS DIVERSES.<br/> Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.</p>""",
                       )
        self.assertEquals(res, """<p>TITRE VI :<hr class="spacer"/> <hr/>DISPOSITIONS DIVERSES.<br/> Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.</p>""")


        html_in1 = """<p>TITRE VI :<hr class="spacer"/> <hr/>DISPOSITIONS
        DIVERSES.<br/> Chapitre III : Informations sur les marchés. Section 1 :
        Observatoire économique de l'achat public.</p>"""
        html_out1 = """<p>TITRE VI :<hr class="spacer"/> <hr/>DISPOSITIONS
        DIVERSES.<br/> Chapitre III : Informations sur les marchés. Section 1 :
        Observatoire économique de l'achat public.</p>"""

        html_in2 = """debian <div>GPL <span class="myclass" >license</span></di>"""
        html_out2 = """debian <div>GPL <span class="myclass">license</span></div>"""

        html_sanitizer = XhtmlSanitizer()
        html_sanitizer.feed(html_in1)
        res = html_sanitizer.getResult()
        self.assertEquals(res, html_out1)
        html_sanitizer.reset()
        html_sanitizer.feed(html_in2)
        res = html_sanitizer.getResult()
        self.assertEquals(res, html_out2)

    def testHtmlBody(self):
        self.assertEquals(getHtmlBody(''), '')


    def testHtmlSanitizing(self):
        res = sanitize('ftgyuhjik', sgml=True)
        self.assertEquals(res, 'ftgyuhjik')

        # Broken tags should not break the sanitizer.
        # A better sanitizer would sanitizes those broken tags instead of giving
        # up and returning the text uncleaned.
##         res = sanitize('<!12345>', sgml=True)
##         self.assertEquals(res, '<!12345>')
##         res = sanitize('<foo@bar.org>', sgml=True)
##         self.assertEquals(res, '<foo@bar.org>')
##         res = sanitize('AAAAAAAA <foo@bar.org>BB', sgml=True)
##         self.assertEquals(res, 'AAAAAAAA <foo@bar.org>BB')

        res = sanitize('<a>ftgyuhjik</a>', sgml=True)
        self.assertEquals(res, '<a>ftgyuhjik</a>')

        res = sanitize('AAA<br>BBB', sgml=True)
        self.assertEquals(res, 'AAA<br>BBB')

        res = sanitize('<html>ftgyuhjik</html>', sgml=True)
        self.assertEquals(res, 'ftgyuhjik')

        res = sanitize('AAA<html>ftgyuhjik</html>BB', sgml=True)
        self.assertEquals(res, 'AAAftgyuhjikBB')

        res = sanitize('<html>ftg<strong>yuh</strong> jik</html>',
                       sgml=True)
        self.assertEquals(res, 'ftg<strong>yuh</strong> jik')

        res = sanitize('<html>ftg<strong>yuh  </strong>jik</html>',
                       sgml=True)
        self.assertEquals(res, 'ftg<strong>yuh  </strong>jik')

        res = sanitize('yu<script langage="javascript">h</script></c>',
                       sgml=True)
        self.assertEquals(res, 'yuh')

        res = sanitize('dfrtgyhju<span class="myclass">ghj</span>',
                       sgml=True)
        self.assertEquals(res, 'dfrtgyhju<span class="myclass">ghj</span>')

        res = sanitize('dfrtgyhju<span class="myclass" >ghj</span>',
                       sgml=True)
        self.assertEquals(res, 'dfrtgyhju<span class="myclass">ghj</span>')

        res = sanitize('debian <div>fsf dfrtgyhju<span class="myclass" >ghj</span></di>',
                       sgml=True)
        self.assertEquals(res, 'debian <div>fsf dfrtgyhju<span class="myclass">ghj</span></div>')

        res = sanitize('<a href="../../../../../../../view" accesskey="U" title="wii" _base_href="http://localhost:29980/cps2/sections/wii/we/">wii</a>',
                       sgml=True)
        self.assertEquals(res, '<a href="../../../../../../../view" title="wii" _base_href="http://localhost:29980/cps2/sections/wii/we/">wii</a>')

        markup = '<address>Paris</address><blockquote><p>Paix longue</p></blockquote>'
        res = sanitize(markup, sgml=True)
        self.assertEquals(res, markup)

        markup = '<q>Paix courte</q><cite>22.3.4</cite><abbr>CNRS</abbr><acronym>LASER</acronym>'
        res = sanitize(markup, sgml=True)
        self.assertEquals(res, markup)

        # Testing tag replacements
        res = sanitize('ftg<b>yuh</b>jik abcde', sgml=True)
        self.assertEquals(res, 'ftg<strong>yuh</strong>jik abcde')

        res = sanitize('<span>ftg<b>yuh</b>jik abcde', sgml=True)
        self.assertEquals(res, '<span>ftg<strong>yuh</strong>jik abcde</span>')

        res = sanitize('<html>ftg<b>yuh</b>jik</html>', sgml=True)
        self.assertEquals(res, 'ftg<strong>yuh</strong>jik')

        res = sanitize('ftg<i>yuh</i>jik', sgml=True)
        self.assertEquals(res, 'ftg<em>yuh</em>jik')

        res = sanitize('ftg<i>yuh </i>jik', sgml=True)
        self.assertEquals(res, 'ftg<em>yuh </em>jik')

        res = sanitize('ftg<i>  yuh</i>jik', sgml=True)
        self.assertEquals(res, 'ftg<em>  yuh</em>jik')

        # Testing entities
        inp = '&laquo;&agrave;&raquo'
        self.assertEquals(sanitize(inp, sgml=True), inp)

        # Testing removals of all HTML tags
        res = sanitize("<p>TITRE VI : DISPOSITIONS DIVERSES.<P> Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.</p>",
                       tags_to_keep=[])
        self.assertEquals(res, "TITRE VI : DISPOSITIONS DIVERSES. Chapitre III : Informations sur les marchés. Section 1 : Observatoire économique de l'achat public.")

        html_in1 = """<p>TITRE VI : DISPOSITIONS
        DIVERSES.<br> Chapitre III :<p> Informations sur les marchés. Section 1 :
        Observatoire économique de l'achat public.</p>"""
        html_out1 = """<p>TITRE VI : DISPOSITIONS
        DIVERSES.<br> Chapitre III :<p> Informations sur les marchés. Section 1 :
        Observatoire économique de l'achat public.</p>"""

        html_in2 = """debian <div>GPL <span class="myclass" >license</span></di>"""
        html_out2 = """debian <div>GPL <span class="myclass">license</span></div>"""

        html_sanitizer = HTMLSanitizer()
        html_sanitizer.feed(html_in1)
        res = html_sanitizer.getResult()
        self.assertEquals(res, html_out1)
        html_sanitizer.reset()
        html_sanitizer.feed(html_in2)
        res = html_sanitizer.getResult()
        self.assertEquals(res, html_out2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
