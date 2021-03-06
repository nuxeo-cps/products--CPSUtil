# (C) Copyright 2005-2009 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Olivier Grisel <og@nuxeo.com>
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
# $Id: html.py 53128 2008-11-23 22:27:28Z madarche $
"""Utility functions for email handling (i18n, etc.).
"""

import logging
import re
import smtplib
import socket

from email import Encoders
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import make_msgid

from Products.CMFCore.utils import getToolByName
from text import get_final_encoding

logger = logging.getLogger('Products.CPSUtil.mail')

class retransform:
    """abstract class for regex transforms (re.sub wrapper)"""

    inputs  = ('text/html',)
    output = 'text/plain'

    def __init__(self, name, *args):
        self.__name__ = name
        self.regexes = []
        for pat, repl in args:
            self.addRegex(pat, repl)

    def name(self):
        return self.__name__

    def addRegex(self, pat, repl):
        r = re.compile(pat)
        self.regexes.append((r, repl))

    def convert(self, orig):
        for r, repl in self.regexes:
            orig = r.sub(repl, orig)
        return orig


# simple html to text converter for email bodies
# GR: taken almost as is from CPSCourrier.utils, but don't remember why
# send_mail didn't rely on CPSUtil.html.htmlToText in the first place.

_html_converter = retransform("html_to_text",
                       ('<br/?>', '\n'),
                       ('<script [^>]>.*</script>(?im)', ''),
                       ('<style [^>]>.*</style>(?im)', ''),
                       ('<head [^>]>.*</head>(?im)', ''),
                       ('<[^>]*>(?i)(?m)', ''),
                       )

def html_to_text(html_data):
    return _html_converter.convert(html_data)

def make_cid(base):
    """Return an RFC 2392 compliant Content-ID, stripped of the <> brackets."""
    # RFC treats message ids and content ids exactly in the same way and
    # refers to RFC 822 for syntax.
    return make_msgid(base)[1:-1]

def _make_html_part(body, encoding, related_parts=None):
    html_part = MIMEText(body, _subtype='html', _charset=encoding)
    if not related_parts:
        return html_part

    res = MIMEMultipart(_subtype='related')
    res.attach(html_part)
    for cid, part in related_parts.items():
        sub_part = _make_file_part(part['content-type'], part['data'])
        sub_part.add_header('Content-Disposition', 'inline',
                            filename=part['filename'])
        sub_part.add_header('Content-Id', '<%s>' % cid)
        res.attach(sub_part)
    return res

def _make_file_part(content_type, data):
    if content_type is None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        content_type = 'application/octet-stream'
    maintype, subtype = content_type.split('/', 1)
    if maintype == 'text':
        sub_msg = MIMEText(data, _subtype=subtype)
    elif maintype == 'image':
        sub_msg = MIMEImage(data, _subtype=subtype)
    elif maintype == 'audio':
        sub_msg = MIMEAudio(data, _subtype=subtype)
    else:
        sub_msg = MIMEBase(maintype, subtype)
        sub_msg.set_payload(data)
        # Encode the payload using Base64
        Encoders.encode_base64(sub_msg)
    return sub_msg

def _encode_header(header, encoding):
    """Encode header according to RFC 2047 for non-ASCII subjects.

    >>> _encode_header(u'this is pure ascii', 'whatever')
    'this is pure ascii'
    >>> header = _encode_header(u'\xe9', 'latin-1')
    >>> header.encode()
    '=?iso-8859-1?q?=E9?='
    """
    try:
        return str(header)
    except UnicodeEncodeError:
        return Header(header, encoding)

ADDRESS_REGEXP = re.compile(r'(.*) <(.*?)>')

def _encode_address(address, encoding, split_form=False):
    """Encode an address for From or To headers.

    If split_form is True, address is expected to be a tuple (fullname, email).
    Otherwise, it's expected to be a unicode string in FullName <email> form.

    Inspired from http://www.velocityreviews.com/forums/t752726-generate-and-send-mail-with-python-tutorial.html

    >>> _encode_address(u"Jo\xe9 <joe@example.com>", 'latin-1')
    '=?iso-8859-1?q?Jo=E9?= <joe@example.com>'
    >>> _encode_address((u"Jo\xe9", "joe@example.com"), 'latin-1',
    ...                 split_form=True)
    '=?iso-8859-1?q?Jo=E9?= <joe@example.com>'
    >>> _encode_address('cps@example.com', 'latin-1')
    'cps@example.com'
    """
    if split_form:
        fullname, email = address
    else:
        m = ADDRESS_REGEXP.match(address)
        if m is None:
            # assumed to be a pure email address, no need to encode
            return address
        fullname, email = m.group(1).strip(), m.group(2)
    try:
        str(fullname)
    except UnicodeError:
        fullname = Header(fullname, encoding).encode()
    return '%s <%s>' % (fullname, str(email))




def send_mail(context, mto, mfrom, subject, body, mcc=(), mbcc=(),
              attachments=(), related_parts=None,
              encoding=None, plain_text=True, additional_headers=()):
    """Send a mail

    mto is the user-level Mail To. It can be a string, or list/tuple of strings.
        It can also be None, or empty, provided there are Ccs or Bccs.
    mcc (Mail Cc) and mbcc (Mail Bcc) can be strings or list/tuples of strings.

    body is plain text or html according to the plain_text kwarg

    Optional attachments are triples (filename, content-type, data) tuples.
    additional_headers are pairs (name, value), where data is either a string
    or an object implementing the file API.

    If optional related_parts dict is present and body is html, it's used in
    a multipart/related MIME construct. The keys are content ids, values are
    triples like attachments.

    This function does not do any error handling besides re-casting and logging
    if the Mailhost fails to send it properly.
    This will be handled by the callers along with the redirect if needed.
    """
    if encoding is None:
        encoding = get_final_encoding(context)
    if related_parts is None:
        related_parts = {}
    mailhost = getToolByName(context, 'MailHost')
    attachments = list(attachments)

    # prepare main content
    content_type = plain_text and 'text/plain' or 'text/html'

    if isinstance(body, unicode):
        body = body.encode(encoding)

    if plain_text:
        main_msg = MIMEText(body, _subtype='plain', _charset=encoding)
    else:
        alt_html = _make_html_part(body, encoding, related_parts=related_parts)
        alt_plain = MIMEText(html_to_text(body), _charset=encoding)
        main_msg = MIMEMultipart(_subtype='alternative',
                                 _subparts=[alt_plain, alt_html])

    if attachments:
        msg = MIMEMultipart()
        msg.attach(main_msg)
    else:
        msg = main_msg

    COMMASPACE = ', '

    # Headers
    msg['Subject'] = _encode_header(subject, encoding)
    msg['From'] = _encode_address(mfrom, encoding)

    if not mto:
        mto = []
    if isinstance(mto, basestring):
        mto = [mto]

    msg['To'] = COMMASPACE.join([_encode_address(to, encoding) for to in mto])

    if mcc:
        mcc = isinstance(mcc, basestring) and (mcc,) or mcc
        msg['Cc'] = COMMASPACE.join(
            [_encode_address(cc, encoding) for cc in mcc])
        if not mto:
            # use first Cc as (non header) mail-to
            mto = mcc[0]
    if mbcc:
        # Don't put Bcc in headers otherwise they'd get transferred
        if isinstance(mbcc, basestring):
            mbcc = [mbcc]
        mto.extend(mbcc)

    for key, value in additional_headers:
        msg[key] = _encode_header(value, encoding)

    if isinstance(subject, unicode):
        msg.preamble = subject.encode(encoding)
    else:
        msg.preamble = subject

    # Guarantees the message ends in a newline
    msg.epilogue = ''

    # attachment management (if any)
    for title, ctype, data in attachments:
        sub_msg = _make_file_part(title, ctype, data)
        # Set the filename parameter
        sub_msg.add_header('Content-Disposition', 'attachment',
                           filename=title)
        msg.attach(sub_msg)

    # loggin string
    attachment_log = list((title, ctype) for title, ctype, _ in attachments)
    related_log = list((rel['filename'], rel['content-type'])
                       for rel in related_parts.values())
    log_str = 'to: %r, from: %r, subject: %r, body: %r, rel: %r, att: %r' % (
        mto, mfrom, subject, body, related_log, attachment_log)
    logger.debug('sending email %s', log_str)

    # sending and error casting
    if not mto:
        raise ValueError("Empty final list of recipients address")
    try:
        return mailhost._send(mfrom, mto, msg.as_string())
    # if anything went wrong: log the error for the admin and raise an exception
    # of type IOError or ValueError that will be catched by the callers in
    # order to build a friendly user message
    except (socket.error, smtplib.SMTPServerDisconnected), e:
        logger.error("error sending email %s" % log_str)
        raise IOError(e)
    except smtplib.SMTPRecipientsRefused, e:
        logger.error("error sending email %s" % log_str)
        raise ValueError('invalid_recipients_address')
    except smtplib.SMTPSenderRefused, e:
        logger.error("error sending email %s" % log_str)
        raise ValueError('invalid_sender_address')
