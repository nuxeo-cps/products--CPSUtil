=================================
CPS Developer Documentation Tools
=================================

:Author: Dave Kuhlman <dkuhlman@rexx.com> <http://www.rexx.com/~dkuhlman>

.. sectnum::    :depth: 4
.. contents::   :depth: 4


Description
===========

This tool (build_cps_doc.py) can be used to generate documentation
from the .txt files in /doc/ directories.  It is capable of
producing the following output:

- An HTML file for each .txt file in the listed directories.

- A PDF file for each .txt file in the listed directories.

- Index files for all generated documents in the listed
  directories.  The index files are: index.txt, index.html,
  index_pdf.txt, index_pdf.pdf.

- Distribution files for all listed documentation as either
  a gzipped tar file or a Zip file.

Uses -- Although this tool was initially intended to be used to
process the documents in the /doc/ directories in the CPS
distribution, it is applicable whenever:

- Documents are in a set of directories, usually sub-directories
  of the directory from which this tool is run.

- The source documents have names with the extension .txt.

- The source documents contain reStructuredText.  The document
  title is on the first three lines of the source document and has
  over and under-adornment with the "=" character.

- The directories are described in an XML file with the same
  element structure as ``doc_directories.xml``.


Installation
============

Unroll the doc_tools distribution in your Products directory with
something like the following::

    $ cd my_zope_instance/Products
    $ unzip doc_tools-1.0a.zip


Requirements
------------

The following are required:

- Docutils

- pdflatex, if you want to generate PDF.

- Either ElementTree or lxml.


How to Use It
=============

To see help on build_cps_doc.py, run::

    $ doc_tools/build_cps_doc.py --help


Build target documents (.html and .pdf)
---------------------------------------

The -w and -p flags build HTML and PDF documents, respectively.

Typical usage is::

    $ cd my_zope_instance/Products
    $ doc_tools/build_cps_doc.py -f -i -w -p -x doc_tools/doc_directories.xml

which will build:

- HTML for .txt files in all directories listed in
  doc_tools/doc_directories.xml.
- PDF for .txt files in all directories listed in
  doc_tools/doc_directories.xml.
- The index files with links to generated target documents.  The
  generated index files are:

  + For HTML: index.txt and index.html
  + For HTML: index_pdf.txt and index_pdf.pdf

A few additional notes:

- There are notes on the format of the directories file in
  doc_tools/doc_directories.xml.

- There is a restriction on the documents included in the index
  files.  The document titles in these files must be on the first
  three (3) lines of the file and must have an over and under
  adornment with the character "=".  This is because (1) I was too
  lazy to use the proper Docutils parsing tool to extract the
  document title correctly and (2) I want to try to encourage this
  consistency across documents anyway.

- Unconditionally forcing building of documents -- build_cps_doc.py
  checks the dates of files and only builds HTML and PDF files
  when they are out of date.  If you wish to force building of all
  files, use the command line flag: -u/--unconditional-update.

- You can list directories to be processed on the command line or
  in a separate file.  See the -x/--xml-directories command line flag
  and notes in the file doc_directories.xml.  Use of a directories
  file such as doc_directories.xml is recommended, since doing so
  enables you specify a title and descriptive text for each product.


Build index files
-----------------

The -i flag builds index documents.

Typical usage is::

    $ cd my_zope_instance/Products
    $ doc_tools/build_cps_doc.py -f -i -x doc_tools/doc_directories.xml

Which will build index files with links to generated target
documents.  The generated index files are:

- For HTML: index.txt and index.html
- For PDF: index_pdf.txt and index_pdf.pdf

You may also combine the -i, -w, and -p flags.


Build a distribution file
-------------------------

You can build either a Zip file or a gzipped tar file.

Typical usage for these tasks is::

    $ doc_tools/build_cps_doc.py -z cps_docs.zip -x doc_tools/doc_directories.xml

or::

    $ doc_tools/build_cps_doc.py -g cps_docs.tar.gz -x doc_tools/doc_directories.xml

You can also do any one of the following::

    $ doc_tools/build_cps_doc.py -g pkg.tar.gz --dist-include="html" -x doc_tools/doc_directories.xml
    $ doc_tools/build_cps_doc.py -z pkg.zip --dist-include="html" -x doc_tools/doc_directories.xml
    $ doc_tools/build_cps_doc.py -g pkg.tar.gz --dist-include="pdf" -x doc_tools/doc_directories.xml
    $ doc_tools/build_cps_doc.py -z pkg.zip --dist-include="pdf" -x doc_tools/doc_directories.xml
    $ doc_tools/build_cps_doc.py -g pkg.tar.gz --dist-include="html:pdf" -x doc_tools/doc_directories.xml
    $ doc_tools/build_cps_doc.py -z pkg.zip --dist-include="html:pdf" -x doc_tools/doc_directories.xml

to select the type of generated files to be included in the
distribution file.


The directories description file
--------------------------------

See file ``doc_directories.xml`` for a sample of the XML file that
describes the directories to be processed.

Each <directory> element in that file specifies a product whose
documentation is to be processed.  These elements are of the
form::

  <directory>
    <path>./CPSBlog/doc</path>
    <title>CPSBlog</title>
    <text>A simple Blog product for CPS.
    </text>
  </directory>

Where:

- *path* specifies the path to the directory containing the
  product's documentation files.

- *title* gives a title.  It is used in the index files.

- *text* provides a description of and comments on the product.
  This text is included in the index files. It should be valid
  reST.



.. Emacs
.. Local Variables:
.. mode: rst
.. End:
.. Vim
.. vim: set filetype=rst:

