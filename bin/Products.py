# (C) Copyright 2005 Nuxeo SAS <http://nuxeo.com>
# Authors:
# Olivier Grisel <og@nuxeo.com>
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
"""Fake Products - simple fake Products module to fix import statements in IDEs

Goal
====

Some IDEs and advanced editors (such as Eclipse+Pydev or vim) do not understand
the 'from Products.MyProduct.MyModule import MyClass' syntax because Prodcuts is
not a true python package (it is a virtual package that merges packages from
several directories). This fake module aims at to inline dev tools like
intellisense completion and errors checkers feel alright when working with zope
code.

Usage
=====

Put this file in a folder at the begining of the PYTHONPATH of your
favorite editor::

    $ PYTHONPATH=/path/to/this/file ; vim

Do not forget to adjust the __path__ variable to fit your setup.

WARNING!
========

You should not put this in your regular PYTHONPATH when running zope. I feel to
lazy to think whether this can harm your server or not.

WARNING #2!
===========

Importing this file will automatically import all the Products from the __path__
list. Be sure this will not produce unwanted side effects before running it.
"""

import os
from os.path import join
import sys
from pkgutil import extend_path

SOFTWARE_HOME = join('/', 'opt', 'Zope-2.8')
INSTANCE_HOME = join('~', 'instances', 'zope')
INSTANCE_HOME = os.path.expanduser(INSTANCE_HOME)

# basic debug info
VERBOSE = False

__path__ = [
    join(SOFTWARE_HOME, 'lib', 'python','Products'),
    join(INSTANCE_HOME, 'Products'),
    ]

# Initially: no products loaded
__all__ = []

# Fake __ac_permissions
__ac_permissions__ = ()

# We will need the standard Zope modules to be able to import Products
sys.path.insert(0, join(SOFTWARE_HOME, 'lib', 'python'))
g = globals()

clean_sys_path = False

for products_dir in __path__:
    for product_id in os.listdir(products_dir):
        if products_dir not in sys.path:
            # temporary adding this dir to the sys.path
            sys.path.insert(0, products_dir)
            clean_sys_path = products_dir

        product_path = join(products_dir, product_id)
        if os.path.exists(join(product_path, '__init__.py')):
            if VERBOSE:
                print "adding", product_path
            product = __import__(product_id, g, g, ('__doc__',))
            g[product_id] = product
            __all__.append(product)

        if clean_sys_path:
            # cleaning the sys.path
            sys.path.remove(clean_sys_path)
            clean_sys_path = False



