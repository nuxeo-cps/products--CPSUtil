# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
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
"""File utilities.
"""

import rfc822
from StringIO import StringIO # cStringIO is not deepcopy-able
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import File


class PersistableFileUpload(FileUpload):
    """A FileUpload that can be persisted and deepcopied.

    It has the whole file in memory as a string though.
    """
    def __init__(self, fileupload):
        fileupload.seek(0)
        self.file = StringIO(fileupload.read())
        headers = fileupload.headers
        if isinstance(headers, rfc822.Message):
            headers = headers.dict
        self.headers = headers
        self.filename = fileupload.filename
    def read(self, *args):
        return self.file.read(*args)
    def readline(self, *args):
        return self.file.readline(*args)
    def readlines(self, *args):
        return self.file.readlines(*args)
    def seek(self, *args):
        return self.file.seek(*args)
    def tell(self, *args):
        return self.file.tell(*args)
    def close(self):
        return self.file.close()
    # also: 'fileno', 'flush', 'isatty', 'truncate', 'write', 'writelines'

def persistentFixup(ob):
    """Make sure an object is persistable in a session

    Fixes up FileUploads, which are objects holding references
    to bound functions and file objects and are thus not picklable.

    Recurses into lists, tuples and dicts.
    """
    if isinstance(ob, FileUpload):
        if not isinstance(ob, PersistableFileUpload):
            ob = PersistableFileUpload(ob)
    elif isinstance(ob, list):
        ob[:] = [persistentFixup(i) for i in ob]
    elif isinstance(ob, tuple):
        ob = tuple([persistentFixup(i) for i in ob])
    elif isinstance(ob, dict):
        for k, v in ob.iteritems():
            ob[k] = persistentFixup(v)
    return ob


class SimpleFieldStorage(object):
    """A simple FieldStorage to hold a file.
    """
    def __init__(self, file, filename, headers):
        self.file = file
        self.filename = filename
        self.headers = headers


class OFSFileIO(object):
    """An OFS.File object turned into a file.

    Only a few methods are implemented.
    """
    def __init__(self, ofsfile):
        self.data = ofsfile.data
        self.len = ofsfile.size
        self.pos = 0

    def read(self, n=-1):
        """Read at most n bytes from the file.

        Returns a string.
        """
        data = self.data
        pos = self.pos
        if isinstance(data, str):
            if n < 0 or pos+n > self.len:
                n = self.len - pos
            self.pos += n
            return data[pos:self.pos]
        else:
            # a Pdata
            res = ''.join(readPdata(data, pos, n))
            self.pos += len(res)
            return res

    def tell(self):
        return self.pos

    def seek(self, pos, mode=0):
        if mode == 1:
            pos += self.pos
        elif mode == 2:
            pos += self.len
        self.pos = max(0, pos)


def readPdata(pdata, pos, n=-1):
    """Read at most n bytes from a Pdata starting at offset pos.

    Returns a list of strings.
    """
    if pdata is None:
        return []
    l = len(pdata.data)
    if pos >= l:
        return readPdata(pdata.next, pos-l, n)
    if n < 0:
        res = readPdata(pdata.next, 0, -1)
        res.insert(0, pdata.data[pos:])
        return res
    if pos+n > l:
        res = readPdata(pdata.next, 0, n-l+pos)
        n = l-pos
    else:
        res = []
    res.insert(0, pdata.data[pos:pos+n])
    return res


def makeFileUploadFromOFSFile(ofsfile, filename=None):
    """Make a file upload from an OFS.File object.
    """
    if ofsfile is None:
        return None
    io = OFSFileIO(ofsfile)
    if filename is None:
        filename = ofsfile.title
    headers = {'content-type': ofsfile.content_type}
    fs = SimpleFieldStorage(io, filename, headers)
    return FileUpload(fs)
