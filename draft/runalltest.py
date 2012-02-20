#
#cgoutte 2012
#Anybox
#TODO :  put licence
#
import pdb
import os
import glob
import optparse
import multiprocessing
from subprocess import Popen, PIPE
import shlex
import sys
from time import time
"""
This file aims to replace the previous runalltest shell script
!-for now i (cgoutte) try to translate the file from shell script to python
this scripts [runalltests] can (could) be found in CPSUtils/bin/runalltests and
 aims to test all cps products one at the time using a single command
Products that should be tested should be either in an uppder directory name products or provided
"""

def f(s):
    os.system(s)

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
    Parser = optparse.OptionParser()
    Parser.add_option('-i', '--integration', action = 'store_true'
                        , default = False,
                        help = 'use if you want to run integration' +
                        'tests', dest = 'integration')
    Parser.add_option('-y', '--yes', action = 'store_true', default = False,
                        help = "There seems to be another attribute, in bundle manifest file"

    Parser.add_option('-p', '--processes', dest = 'nbprocesses',
                        default = 1, help = 'this option allows you to choose how '+
                        'many processes you would like to use, this may '+
                        'enhance time perfomances'
                        )
    Parser.add_option('-b', '--Bundle_dir', dest = 'bundle_dir', default = 'Products',
                        help = 'Name of the (upper) folder that contains (Zope)' +
                        'products which should be tested')  

    options, args = Parser.parse_args()
    while not options.bundle_dir in os.listdir(os.getcwd()):
        os.chdir('..')

    if options.integration:
        attrib_filter = '--attributes-filter=testing:integration'
    
    else :
        attrib_filter = '--attributes-filter=testing:continuous'
    conf = 'etc/zope.conf'
    if 'test.conf' in os.listdir('etc'):
        conf = 'etc/test.conf'
    
    if 'BUNDLE_MANIFEST.xml' in os.listdir('Products'):
        cmd = ( 'hgbundler clones-list' 
       + ' ' + '--bundle-dir='+options.bundle_dir
       + ' ' + attrib_filter 
       + ' ' + '--toplevel-only')
        hgb = Popen(shlex.split(cmd), stdout = PIPE)
        prods = hgb.stdout.read().split('\n')[0:-1]
        #since we have an empty line at the end of hgbundler's stdout

    else:
        subdirs = glob.glob('./Products/CPS*/__init__.py')
        prods = [rep.split('/')[2] for rep in subdirs]     

    dirs = os.listdir(options.Bundle_dir)
    tasks = list()

    for name  in prods :
        proddir = 'Products'+'/'+name
        print proddir 
        c1 = 'bin/zopectl test --config-file=' + conf + ' --dir ' 
        tasks.append(c1 + proddir)

    t0=time()    

    for command in tasks :        
        t = time()        
        proc = Popen(shlex.split(command),bufsize = -1, stdout = PIPE, stderr = PIPE)
        print('running command ' + command)
        sout, serr = proc.communicate()
        print('done in %.3f second(s)' % (time() - t))

    print('='*80)
    print('+' + ' Ran all theses tests in %.3f second(s)' % (time() - t0) )
    print('='*80)    
