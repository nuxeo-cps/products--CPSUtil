#!/usr/bin/env python
# (C) Copyright 2010 CPS-CMS Community <http://cps-cms.org/>
# Authors:
# Dave Kuhlman <dkuhlman@cutter.rexx.com>
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
"""
Build CPS documentation.

Produces HTML and PDF.

Also, can generate index files.

See README.txt or README.html for more information.

Typical usage:

   $ cd my_instance/Products
   $ doc_tools/build_cps_doc.py -i -w -p doc_tools/doc_directories.txt


usage:
    python build_cps_doc.py [options] [directory, directory, ... ]
examples:
    python build_cps_doc.py -p -w ./CPSDefault/doc ./CPSDesignerThemes/doc
    doc_tools/build_cps_doc.py -f -i -w -p -d doc_tools/doc_directories.txt


options:
  -h, --help            show this help message and exit
  -p, --pdf             generate PDF files
  -w, --html            generate (Web) HTML files
  -i, --index           generate index files
  -x XMLDIRECTORIES, --xml-directories=XMLDIRECTORIES
                        read list of directories from XML FILENAME
  -z ZIPFILE, --zip-file=ZIPFILE
                        create .zip file of all source and target documents
  -g TARFILE, --gzip-tar-file=TARFILE
                        create gzip tar file of all source and target
                        documents
  --dist-include=DISTRIBUTIONINCLUDE
                        include in distribution, e.g. "html", "pdf", or
                        (default) "html:pdf"
  -s STYLESHEETPATH, --stylesheet=STYLESHEETPATH
                        stylesheet (default: ./CPSDefault/doc/cps_doc.css)
  -q, --quiet           run in quiet mode
  -f, --force           force over-write of index files without asking
  -u, --unconditional-update
                        unconditional update: always build target (html, pdf)
                        even if not missing or out-of-date

"""

import sys
import os
import glob
import re
from optparse import OptionParser
from docutils.core import publish_file
import zipfile
import tarfile


#
# Constants and globals:
#

StylesheetPath = './CPSDefault/doc/cps_doc.css'
PdfCommandTmpl = 'pdflatex %s.tex'

BuildingMessage = '''
##
## Building %s
##'''


HtmlIndexFileName = 'index%s'
PdfIndexFileName = 'index_pdf%s'

IndexHeader = '''\
=====================
CPS 3.6 Documentation
=====================

.. sectnum::    :depth: 4
.. contents::   :depth: 4


Introduction
============
CPS is made of products for the Zope 2 application server.
This document aims at providing links to documentation for each of these
products.

CPS products are organized in three distributions:

- `CPS-3-base`: the minimal set of products up to the first fully integrated
  application (CPSDefault).
- `CPS-3`, also known as `CPS-Standard` and formerly `CPS-Platform`: a superset
  of CPS-3-base, adding some commonly used extensions.
- `CPS-3-full`: the set of all the actively maintained products.

This page follows this structure: first CPS-3-base products (up to CPSDefault),
then CPS-3-standard (up to CPSSharedCalendar) and finally some products from
CPS-3-full.

Additional information can be found at `the cps-cms.org website <http://cps-cms.org>`_.

Older documentation links (some may currently be broken):

- `CPS Project: Documentation <http://www.cps-project.org/sections/documentation>`_

- `CPS Project: For users
  <http://www.cps-project.org/sections/documentation/users>`_

- `CPS Manual - English PDF
  <http://www.cps-project.org/sections/documentation/users/cps-manual-english-pdf/>`_

- `CPS Project: For developers
  <http://www.cps-project.org/sections/documentation/developers>`_

'''
IndexFooter = ''

TitlePattern = re.compile(r'^=*$')
DirectoryPattern = re.compile(r'/(\w*)/')

# ----------------------------------------------------

def generate_html(directories, stylesheetPath, quiet, update):
    """Generate .txt --> .html in each Product directory.
    """
    if not quiet:
        print BuildingMessage % ('HTML', )
    for directory in directories:
        #directory, product = parse_directory(entry)
        path = directory.get_path()
        title = directory.get_title()
        text = directory.get_text()
        if not quiet:
            print '\nProcessing directory: %s' % path
        fileNames = glob.glob('%s/*.txt' % path)
        for fileName in fileNames:
            path, ext = os.path.splitext(fileName)
            baseName = os.path.basename(fileName)
            sourceName = '%s.txt' % path
            targetName = '%s.html' % path
            if check_date(sourceName, targetName, update):
                if not quiet:
                    print '    File: %s --> %s' % (sourceName, targetName, )
                settings_overrides = {
                    'generator': 1,
                    'stylesheet_path': stylesheetPath,
                    'stylesheet': None,
                    'source_url': baseName,
                    }
                publish_file(source_path='%s' % sourceName,
                    destination_path='%s' % targetName,
                    writer_name='html',
                    settings_overrides=settings_overrides)
    print


def generate_pdf(directories, stylesheetPath, quiet, update):
    """Generate .txt --> .pdf in each Product directory.
    """
    if not quiet:
        print BuildingMessage % ('PDF', )
    for directory in directories:
        path = directory.get_path()
        title = directory.get_title()
        text = directory.get_text()
        if not quiet:
            print '\nProcessing directory: %s' % path
        fileNames = glob.glob('%s/*.txt' % path)
        for fileName in fileNames:
            path1, ext = os.path.splitext(fileName)
            baseName = os.path.basename(fileName)
            sourceName = '%s.txt' % path1
            texName = '%s.tex' % path1
            targetName = '%s.pdf' % path1
            if check_date(sourceName, targetName, update):
                if not quiet:
                    print '    File: %s --> %s' % (sourceName, targetName )
                settings_overrides = {
                    'generator': 1,
                    #'stylesheet_path': stylesheetPath,
                    'source_url': baseName,
                    }
                publish_file(source_path='%s' % sourceName,
                    destination_path='%s' % texName,
                    writer_name='latex',
                    settings_overrides=settings_overrides)
                latex_to_pdf(path, baseName)
    print


def generate_zip(directories, zipFileName, force, quiet, distributionInclude):
    """Generate Zip file containing all source and target documents.
    """
    if not check_file(zipFileName, force):
        return
    if not quiet:
        print BuildingMessage % ('Zip file', )
    zipFile = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED)
    distributionInclude = distributionInclude.split(':')
    if 'html' in distributionInclude:
        fileName = HtmlIndexFileName % ('.txt', )
        if os.path.exists(fileName):
            zipFile.write(fileName)
        fileName = HtmlIndexFileName % ('.html', )
        if os.path.exists(fileName):
            zipFile.write(fileName)
    if 'pdf' in distributionInclude:
        fileName = PdfIndexFileName % ('.txt', )
        if os.path.exists(fileName):
            zipFile.write(fileName)
        fileName = PdfIndexFileName % ('.pdf', )
        if os.path.exists(fileName):
            zipFile.write(fileName)
    for directory in directories:
        path = directory.get_path()
        if not quiet:
            print '\nProcessing directory: %s' % path
        fileNames = glob.glob('%s/*.txt' % path)
        for fileName in fileNames:
            zipFile.write(fileName)
        if 'html' in distributionInclude:
            fileNames = glob.glob('%s/*.html' % path)
            for fileName in fileNames:
                zipFile.write(fileName)
        if 'pdf' in distributionInclude:
            fileNames = glob.glob('%s/*.pdf' % path)
            for fileName in fileNames:
                zipFile.write(fileName)
    if not quiet:
        names = zipFile.namelist()
        print '\nZip file contents:'
        for name in names:
            print '    %s' % name
    zipFile.close()


def generate_gzip_tar(directories, tarFileName, force, quiet,
    distributionInclude):
    """Generate gzipped tar file containing all source and target documents.
    """
    if not check_file(tarFileName, force):
        return
    if not quiet:
        print BuildingMessage % ('gzip tar file', )
    tarFile = tarfile.open(tarFileName, 'w:gz')
    distributionInclude = distributionInclude.split(':')
    if 'html' in distributionInclude:
        fileName = HtmlIndexFileName % ('.txt', )
        if os.path.exists(fileName):
            tarFile.add(fileName, recursive=False)
        fileName = HtmlIndexFileName % ('.html', )
        if os.path.exists(fileName):
            tarFile.add(fileName, recursive=False)
    if 'pdf' in distributionInclude:
        fileName = PdfIndexFileName % ('.txt', )
        if os.path.exists(fileName):
            tarFile.add(fileName, recursive=False)
        fileName = PdfIndexFileName % ('.pdf', )
        if os.path.exists(fileName):
            tarFile.add(fileName, recursive=False)
    for directory in directories:
        path = directory.get_path()
        if not quiet:
            print '\nProcessing directory: %s' % path
        fileNames = glob.glob('%s/*.txt' % path)
        for fileName in fileNames:
            tarFile.add(fileName, recursive=False)
        if 'html' in distributionInclude:
            fileNames = glob.glob('%s/*.html' % path)
            for fileName in fileNames:
                tarFile.add(fileName, recursive=False)
        if 'pdf' in distributionInclude:
            fileNames = glob.glob('%s/*.pdf' % path)
            for fileName in fileNames:
                tarFile.add(fileName, recursive=False)
    if not quiet:
        names = tarFile.getnames()
        print '\ntar file contents:'
        for name in names:
            print '    %s' % name
    tarFile.close()


def generate_html_index(directories, stylesheetPath, force, quiet):
    """Generate HTML index (.txt and .html) for all listed Products.
    The document title must have over and under adornment with "=" in
        order to be included.
    """
    indexFileName = HtmlIndexFileName % '.txt'
    if not check_file(indexFileName, force):
        return
    if not quiet:
        print 'Generating index file: %s' % (indexFileName, )
    indexFile = file(indexFileName, 'w')
    indexFile.write(IndexHeader)
    for directory in directories:
        path = directory.get_path()
        title = directory.get_title()
        text = directory.get_text()
        s1 = '%s\n' % (title, )
        len1 = len(s1) - 1
        indexFile.write(s1)
        s1 = ('=' * len1) + '\n\n'
        indexFile.write(s1)
        if text:
            indexFile.write(text)
            indexFile.write('\n')
        indexFile.write('Contents:\n\n')
        fileNames = glob.glob(path+'/*.txt')
        for fileName in fileNames:
            infile = file(fileName, 'r')
            line1 = infile.readline()
            line2 = infile.readline()
            line3 = infile.readline()
            infile.close()
            if TitlePattern.search(line1) and TitlePattern.search(line3):
                title = line2.strip()
                path = os.path.splitext(fileName)[0] + '.html'
                s1 = '- `%s <%s>`_\n' % (title, path )
                indexFile.write(s1)
        indexFile.write('\n')
    indexFile.write(IndexFooter)
    indexFile.close()
    path = HtmlIndexFileName % ''
    if not quiet:
        print '    File: %s.txt --> %s.html' % (path, path, )
    settings_overrides = {
        'generator': 1,
        'stylesheet_path': stylesheetPath,
        'stylesheet': None,
        'source_url': indexFileName,
        }
    publish_file(source_path='%s.txt' % path,
        destination_path='%s.html' % path,
        writer_name='html',
        settings_overrides=settings_overrides)


def generate_pdf_index(directories, stylesheetPath, force, quiet):
    """Generate PDF index (.txt and .pdf) for all listed Products.
    The document title must have over and under adornment with "=" in
        order to be included.
    """
    indexFileName = PdfIndexFileName % '.txt'
    if not check_file(indexFileName, force):
        return
    if not quiet:
        print 'Generating index file: %s' % (indexFileName, )
    indexFile = file(indexFileName, 'w')
    indexFile.write(IndexHeader)
    for directory in directories:
        path = directory.get_path()
        title = directory.get_title()
        text = directory.get_text()
        s1 = '%s\n' % (title, )
        len1 = len(s1) - 1
        indexFile.write(s1)
        s1 = ('=' * len1) + '\n\n'
        indexFile.write(s1)
        if text:
            indexFile.write(text)
            indexFile.write('\n')
        indexFile.write('Contents:\n\n')
        fileNames = glob.glob(path+'/*.txt')
        for fileName in fileNames:
            infile = file(fileName, 'r')
            line1 = infile.readline()
            line2 = infile.readline()
            line3 = infile.readline()
            infile.close()
            if TitlePattern.search(line1) and TitlePattern.search(line3):
                title = line2.strip()
                path = os.path.splitext(fileName)[0] + '.pdf'
                s1 = '- `%s <%s>`_\n' % (title, path )
                indexFile.write(s1)
        indexFile.write('\n')
    indexFile.write(IndexFooter)
    indexFile.close()
    path = PdfIndexFileName % ''
    if not quiet:
        print '    File: %s.txt --> %s.pdf' % (path, path, )
    settings_overrides = {
        'generator': 1,
        #'stylesheet_path': stylesheetPath,
        'source_url': indexFileName,
        }
    publish_file(source_path='%s.txt' % path,
        destination_path='%s.tex' % path,
        writer_name='latex',
        settings_overrides=settings_overrides)
    latex_to_pdf('./', indexFileName)


def parse_directory(entry):
    """Extract the directory and optional product title from a line
        of text.
    """
    items = entry.split('::')
    if len(items) == 2:
        directory = items[0].strip()
        product = items[1].strip()
    elif len(items) == 1:
        directory = items[0].strip()
        mo = DirectoryPattern.search(directory)
        if mo:
            product = mo.group(1)
        else:
            product = directory
    return (directory, product)


def latex_to_pdf(directory, baseName):
    """Convert a LaTeX file (produced by Docutils) to PDF.

    Note that we need to change current directory to the directory
      containing the LaTeX file because pdflatex does not provide
      a command line flag to specify the output directory.
    """
    cur_dir = os.getcwd()
    os.chdir(directory)
    name, ext = os.path.splitext(baseName)
    command = PdfCommandTmpl % (name, )
    os.popen(command, 'r').read()
    os.remove('%s.tex' % (name, ))
    os.remove('%s.out' % (name, ))
    os.remove('%s.log' % (name, ))
    os.remove('%s.aux' % (name, ))
    os.chdir(cur_dir)


def check_file(fileName, force):
    """Check for and warn about the existence of a file, unless
      force (command line flag) is set.
    """
    if force:
        return True
    if os.path.exists(fileName):
        response = raw_input('File %s exists.  Overwrite? (y/n): ' % fileName)
        if response != 'y':
            return False
        return True
    return True


def check_date(sourceName, targetName, update):
    """Return True if the file needs to be built, specifically
      (1) update is True or (2) the target does not exist
      or (3) the target is out-of-date.
      Else, return False.
    """
    if update:
        return True
    if not os.path.exists(targetName):
        return True
    if os.stat(sourceName)[8] > os.stat(targetName)[8]:
        return True
    return False


def read_directories_file(directoriesFileName):
    """Read a list of directories (and optional product titles) from
      a file.
    Skip lines whose first non-whitespace character is '#'.
    """
    directoriesFile = file(directoriesFileName, 'r')
    directories = []
    for line in directoriesFile:
        line = line.strip()
        if len(line) > 0 and line[0] != '#':
            items = line.split('::')
            if len(items) == 2:
                directory = Directory(items[0].strip(), items[1].strip())
                directories.append(directory)
            elif len(items) == 1:
                # Path and title are the same.
                directory = Directory(items[0].strip(), items[0].strip())
                directories.append(directory)
    directoriesFile.close()
    return directories


class Directory:
    """A simple container class for directory descriptions.
    """
    def __init__(self, path='', title='', text=''):
        self.path = path
        self.title = title
        self.text = text
    def set_path(self, path): self.path = path
    def get_path(self): return self.path
    def set_title(self, title): self.title = title
    def get_title(self): return self.title
    def set_text(self, text): self.text = text
    def get_text(self): return self.text


def read_xml_directories_file(directoriesFileName):
    """Read a list of directories (and optional product titles) from
      an XML file.
    Create and return a list of instances of class Directory.
    """
    try:
        from lxml import etree as ElementTree
        #print '*** using lxml'
    except ImportError, e:
        try:
            from elementtree import ElementTree
            #print '*** using ElementTree'
        except ImportError, e:
            print '***'
            print '*** Error: Must install either ElementTree or lxml.'
            print '***'
            raise
    tree = ElementTree.parse(directoriesFileName)
    root = tree.getroot()
    directories = []
    for child in root.getchildren():
        if child.tag == 'directory':
            path = None
            title = ''
            text = ''
            for child1 in child.getchildren():
                if child1.tag == 'path':
                    path = child1.text
                elif child1.tag == 'title':
                    title = child1.text
                elif child1.tag == 'text':
                    text = child1.text
            if not path:
                print 'Error: missing path'
                sys.exit(-1)
            if not title:
                title = path
            directory = Directory(path, title, text)
            directories.append(directory)
    return directories


def read_args_directories(args):
    """Get a list of directories (and optional product titles) from
      a list of (command line) arguments.
    """
    directories = []
    for arg in args:
        path = arg
        title = arg
        text = ''
        directory = Directory(path, title, text)
        directories.append(directory)
    return directories


USAGE_TEXT = """
    python %prog [options] [directory, directory, ... ]
examples:
    python %prog -p -w ./CPSDefault/doc ./CPSDesignerThemes/doc
    doc_tools/%prog -f -i -w -p -d doc_tools/doc_directories.txt
"""

def usage(parser):
    parser.print_help()
    sys.exit(-1)


def main():
    parser = OptionParser(USAGE_TEXT)
    parser.add_option("-p", "--pdf", action="store_true",
        dest="generatePdf", help="generate PDF files")
    parser.add_option("-w", "--html", action="store_true",
        dest="generateHtml", help="generate (Web) HTML files")
    parser.add_option("-i", "--index", action="store_true",
        dest="generateIndex", help="generate index files")
##    parser.add_option("-d", "--directories", type="string",
##        dest="directories",
##        help="read list of directories (one per line) from FILENAME")
    parser.add_option("-x", "--xml-directories", type="string",
        dest="xmlDirectories",
        help="read list of directories from XML FILENAME")
    parser.add_option("-z", "--zip-file", type="string",
        dest="zipFile",
        help="create .zip file of all source and target documents")
    parser.add_option("-g", "--gzip-tar-file", type="string",
        dest="tarFile",
        help="create gzip tar file of all source and target documents")
    parser.add_option("--dist-include", type="string",
        dest="distributionInclude",
        help='include in distribution, e.g. "html", "pdf", or (default) "html:pdf"')
    parser.add_option("-s", "--stylesheet", type="string",
        dest="stylesheetPath",
        help="stylesheet (default: %s)" % StylesheetPath)
    parser.add_option("-q", "--quiet", action="store_true",
        dest="quiet", help="run in quiet mode")
    parser.add_option("-f", "--force", action="store_true",
        dest="force", help="force over-write of index files without asking")
    parser.add_option("-u", "--unconditional-update", action="store_true",
        dest="update",
        help="unconditional update: always build target (html, pdf) even if not missing or out-of-date")
    (options, args) = parser.parse_args()
##    if options.directories:
##        directories = read_directories_file(options.directories)
    if options.xmlDirectories:
        directories = read_xml_directories_file(options.xmlDirectories)
    else:
        directories = read_args_directories(args)
    stylesheetPath = StylesheetPath
    if options.stylesheetPath:
        stylesheetPath = options.stylesheetPath
    distributionInclude = 'html:pdf'
    if options.distributionInclude:
        distributionInclude = options.distributionInclude
    if options.generateHtml:
        generate_html(directories, stylesheetPath,
            options.quiet, options.update)
#     if options.generatePdf:
#         generate_pdf(directories, stylesheetPath,
#             options.quiet, options.update)
    if options.generateIndex:
        if not options.quiet:
            print BuildingMessage % ('index files', )
        generate_html_index(directories, stylesheetPath,
            options.force, options.quiet)
#        generate_pdf_index(directories, stylesheetPath,
#            options.force, options.quiet)
    if options.zipFile:
        generate_zip(directories, options.zipFile, options.force,
            options.quiet, distributionInclude)
    if options.tarFile:
        generate_gzip_tar(directories, options.tarFile, options.force,
            options.quiet, distributionInclude)
    if not (options.generatePdf or options.generateHtml or \
        options.generateIndex or options.zipFile or \
        options.tarFile):
        usage(parser)


if __name__ == "__main__":
    main()
    #import pdb; pdb.run('main()')
