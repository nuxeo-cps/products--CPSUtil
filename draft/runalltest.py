#
#cgoutte 2012
#Anybox
#TODO :  put licence
#

from os import listdir, system
import glob
import optparse

"""
This file aims to replace the previous runalltest shell script
!-for now i (cgoutte) try to translate the file from shell script to python
this scripts [runalltests] can (could) be found in CPSUtils/bin/runalltests and
 aims to test all cps products one at the time using a single command
"""

if  __name__ == '__main__':
    #print the doc if no args
    #later

    #check if there is a test.conf or fallback to zope.conf
    #store the path to it

    #generate prods list
    # -> Check if there is a bundle manifest file
    # if yes then run `hgbundler clones-list --bundle-dir=Products --attributes-filter=testing:continuous --toplevel-only`
    # else get all Products/CPS*/__init__.py
    
    #To be continued

    conffile='etc/zope.conf'
    if 'test.conf' in os.listdir('etc'):
        conffile = 'etc/test.conf'
    
    if 'BUNDLE_MANIFEST.xml' in os.listdir('Products'):
        prods = os.system('hgbundler clones-list' 
       + ' ' + '--bundle-dir=Products'
       + ' ' + '--attributes-filter=testing:continuous' 
       + ' ' + '--toplevel-only')
    
    else:
        prods = glob.glob('Products/CPS*/__init__.py')

    for name  in prods :
        proddir='Products'+'/'+'name'
        
    
