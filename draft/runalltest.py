#
#cgoutte 2012
#Anybox
#TODO :  put licence
#
import pdb
from os import listdir, system
import glob
import optparse

"""
This file aims to replace the previous runalltest shell script
!-for now i (cgoutte) try to translate the file from shell script to python
this scripts [runalltests] can (could) be found in CPSUtils/bin/runalltests and
 aims to test all cps products one at the time using a single command
"""
class runalltestParser():
        
    def __init__(self):
        self.p = optparse.OptionParser()
        self.p.add_option('-i','--integration',action='store_true'
                        ,default=False,
                        help='use if you want to run integration' +
                        'tests, can\'t be used with -c',dest='integration')
        self.p.add_option('-c','--continuous',dest='continuous',
                        action='store_true',default=False,
                        help='use if you want to run continuous test,'+
                        ' incompatible with -c')
        self.p.add_option('-p','--processes',dest='nbprocesses',
                        default=1,help='this option allows you to choose how '+
                        'many processes you would like to use, this may '+
                        'enhance time perfomances'
                        )

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
    Parser=runalltestParser()   
    Parser.p.parse_args()
        
    conf='etc/zope.conf'
    if 'test.conf' in os.listdir('etc'):
        conf = 'etc/test.conf'
    
    if 'BUNDLE_MANIFEST.xml' in os.listdir('Products'):
        prods = os.system('hgbundler clones-list' 
       + ' ' + '--bundle-dir=Products'
       + ' ' + '--attributes-filter=testing:continuous' 
       + ' ' + '--toplevel-only')
    
    else:
        prods = glob.glob('Products/CPS*/__init__.py')

    for name  in prods :
        proddir='Products'+'/'+'name'
        
    
