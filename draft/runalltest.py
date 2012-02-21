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
import re

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
    parser = optparse.OptionParser()
    parser.add_option('-a', '--all', action = 'store_true'
                        , default = False,
                        help = 'use if you want al the test to be run' +
                        'tests', dest = 'all')

    parser.add_option('-p', '--processes', dest = 'nbprocesses',
                        default = 1, help = 'this option allows you to choose how '+
                        'many processes you would like to use, this may '+
                        'enhance time perfomances'
                        )
    parser.add_option('-b', '--bundle_dir', dest = 'bundle_dir', default = 'Products',
                        help = 'Name of the (upper) folder that contains (Zope)' +
                        'products which should be tested')  
    parser.add_option('-o', '--ouput_dir', dest = 'output_dir',
                       default = 'test_results',
                       help = 'output directory for tests reports relative to instance')

    options, args = parser.parse_args()
    while not options.bundle_dir in os.listdir(os.getcwd()):
        os.chdir('..')
    
    if options.all:
        attrib_filters = ['--attributes-filter=testing:yes','--attributes-filter=testing:continuous']
        
    else :
        attrib_filters = ['--attributes-filter=testing:continuous']

    conf = 'etc/zope.conf'
    if 'test.conf' in os.listdir('etc'):
        conf = 'etc/test.conf'
    
    if 'BUNDLE_MANIFEST.xml' in os.listdir('Products'):
        prods = set()
        for attrib_filter in attrib_filters :       
            cmd = ( 'hgbundler', 'clones-list', 
                     '--bundle-dir='+options.bundle_dir ,
                     attrib_filter , '--toplevel-only' 
                    )
            hgb = Popen((cmd), stdout=PIPE)
            prods = prods.union(hgb.stdout.read().split('\n')[0:-1])
        #since we have an empty line at the end of hgbundler's stdout

    else:
        subdirs = glob.glob('./Products/CPS*/__init__.py')
        prods = [rep.split('/')[2] for rep in subdirs]     

    dirs = os.listdir(options.bundle_dir)
    tasks = list()

    for name  in prods :
        proddir = 'Products'+'/'+name
        print proddir + ' will be tested ' 
        tasks.append(['bin/zopectl', 'test', '--config-file='+conf, '--dir',
                        proddir ])
    
    print('%r components will be tested'%len(tasks))

    t0=time()    

    res_pattern = re.compile("Ran [0-9]* tests with")
    succes_pattern = re.compile("0 failures and 0 errors")
    sum_up = {}

    if not options.output_dir in os.listdir(os.getcwd()):
        os.mkdir(options.output_dir)
    #write files in the proper place

    for task in tasks :        
        t = time()        
        proc = Popen(task,bufsize=-1, stdout=PIPE, stderr=PIPE)
        sout, serr = proc.communicate()
        textout = sout.split('\n')          
        ok = False 
        t1=time()
        
        for l in textout:
             if res_pattern.search(l) and succes_pattern.search(l):
                ok = True
        
        instance =  os.getcwd()
        print task[-1] + '   ',
        if not ok :
            os.chdir(options.output_dir)
            logfile = open(task[-1].split('/')[1] + '.log', 'w')
            logfile.write(sout)
            logfile.close()
            sum_up[task[-1]]='FAIL'
            print 'FAIL',
            print(' in %.3f second(s)' % (t1 - t))

        else :
            sum_up[task[-1]]='OK'
            print 'OK' ,
            print(' in %.3f second(s)' % (t1 - t))

        os.chdir(instance)
        
    s = ''
    s = s+ '+' +'='*79 +'\n'
    s =s + ('|' + ' *** Ran all theses %r tests in %.3f second(s) \o/ ***\n' %
    ( len(tasks) , time() - t0) )
    s = s+ '+' +'='*79 +'\n'
    
    for x, y in sum_up.items():
        s = s +  '|'+ x +' :  ' + y + '\n'
    s = s +'\\'+ 78*'-' +'/'   
    print s
    sum_up_file = open('summup.txt','w')
    sum_up_file.write(s)
    sum_up_file.close()

