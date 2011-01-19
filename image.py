# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
#     G. Racinet <georges@racinet.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import math
from StringIO import StringIO
try:
    import PIL.Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

from Acquisition import aq_base
from OFS.Image import getImageInfo as zopeGetImageInfo
from OFS.Image import Image
from Products.CPSUtil.file import ofsFileHandler

IMG_SZ_FULLSPEC_REGEXP = re.compile(r'^(\d+)x(\d+)$')

IMG_SZ_HEIGHT_REGEXP = re.compile(r'^h(\d+)$')

IMG_SZ_WIDTH_REGEXP = re.compile(r'^w(\d+)$')

IMG_SZ_LARGEST_REGEXP = re.compile(r'^l(\d+)$')

"""High level image manipulating library for CPS."""

class SizeSpecError(ValueError):
    """Special exception for this module's size specifications."""

def imageInfo(img):
    """Return content_type, width, height for img (string, file-like or Image).
    """
    img = aq_base(img)
    if hasattr(img, 'width'):
        return img.content_type, img.width, img.height
    elif hasattr(img, 'seek'):
        img_header = img.read(30)
        img.seek(0)
    elif isinstance(img, str):
        img_header = img[:30]
        img = StringIO(img)

    format, width, height = zopeGetImageInfo(img_header)
    if width < 0 or height < 0 and PIL_OK:
        try:
            img = PIL.Image.open(img)
            width, height = img.size
            if not format:
                format = PIL.Image.MIME.get(img.format,
                                            'application/octet-stream')
        except IOError, e: # TODO a lot
            format = 'application/octet-stream'
            width, height = -1, -1

    if width < 0:
        width = None
    if height < 0:
        height = None

    return format, width, height

def imageGeometry(img):
    """Return width, height for provided image (string, file-like or Image)."""
    return imageInfo(img)[1:]

def _proportionalDim(dim1, target_dim1, dim2):
    """Deduce dimension 2 from the stretch of dim1."""
    return int(math.floor(dim2 * float(target_dim1)/dim1 + 0.5))

def _geometryFromLargest(img, size):
    """Compute width, height from the wished largest dimension."""
    w, h = imageGeometry(img)
    if w > h:
        return size, _proportionalDim(w, size, h)
    else:
        return _proportionalDim(h, size, w), size

def parse_size_spec(spec):
    """Return width, height or raise SizeSpecError.

    where spec can be:
       - full: untransformed
       - 320x200: full size spec (width plus height)
       - w320: width spec: height will keep aspect ratio
       - h200: height spec: width will keep aspect ratio
       - l540: largest dimension spec: wished size of the largest dimension,
                                       keeping aspect ratio




    >>> parse_size_spec('320x200')
    (320, 200)
    >>> parse_size_spec('h500')
    (None, 500)
    >>> parse_size_spec('w1024')
    (1024, None)
    >>> parse_size_spec('l800')
    800
    >>> parse_size_spec('full') is None
    True
    >>> try: parse_size_spec('x1024')
    ... except SizeSpecError, m: print str(m).split(':')[1].strip()
    'x1024'
    """
    spec = spec.strip() # does not hurt
    if spec == 'full':
        return
    m = IMG_SZ_LARGEST_REGEXP.match(spec)
    if m is not None:
        return int(m.group(1))
    m = IMG_SZ_FULLSPEC_REGEXP.match(spec)
    if m is not None:
        return int(m.group(1)), int(m.group(2))
    m = IMG_SZ_WIDTH_REGEXP.match(spec)
    if m is not None:
        return int(m.group(1)), None
    m = IMG_SZ_HEIGHT_REGEXP.match(spec)
    if m is not None:
        return None, int(m.group(1))

    raise SizeSpecError('Incorrect image size specification: %r' % spec)

def parse_size_spec_as_dict(spec):
    """Return a dict suitable as kwargs for e.g., makeSizeSpec

    >>> parse_size_spec_as_dict('320x200')
    {'width': 320, 'height': 200}
    >>> parse_size_spec_as_dict('h500')
    {'height': 500}
    >>> parse_size_spec_as_dict('w1024')
    {'width': 1024}
    >>> parse_size_spec_as_dict('l800')
    {'largest': 800}
    >>> parse_size_spec_as_dict('full')
    {}
    >>> try: parse_size_spec_as_dict('x1024')
    ... except ValueError, m: print str(m).split(':')[1].strip()
    'x1024'
    """
    parsed = parse_size_spec(spec)
    if parsed is None:
        return {}

    if isinstance(parsed, int):
        return dict(largest=parsed)

    return dict((k, v) for k, v in zip(('width', 'height'), parsed)
                if v is not None)

def resized_img_geometry(img, spec):
    """Return corresponding width, height for a size specification on img."""

    sz = parse_size_spec(spec)
    if isinstance(sz, int):
        return _geometryFromLargest(img, sz)

    w, h = imageGeometry(img)

    if spec == 'full':
        return w, h

    rw, rh = sz
    if rw is None:
        return _proportionalDim(h, rh, w), rh
    elif rh is None:
        return rw, _proportionalDim(w, rw, h)

    return rw, rh

def resize(src, width, height, resized_id):
    """Return OFS.Image.Image or None if cannot resize."""

    if not PIL_OK:
        logger.warn("Resizing can't be done until PIL is installed")
        return

    fileio = ofsFileHandler(src)
    try:
        img = PIL.Image.open(fileio)
        newimg = img.resize((width, height), PIL.Image.ANTIALIAS)
        outfile = StringIO()
        newimg.save(outfile, format=img.format)
    except (NameError, IOError, ValueError, SystemError), err:
            logger.warning("Failed to resize image %r (%r). Error: %s), ",
                           src.title, img, err)
            return

    return Image(resized_id, src.title, outfile)



