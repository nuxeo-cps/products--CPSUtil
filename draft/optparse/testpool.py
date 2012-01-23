import multiprocessing
from time import sleep
from pprint import pprint
import pdb
from random import random 
import os


def do_calculation(data):
    """
    Old function to be removed
    """
    i=0
    sname=multiprocessing.current_process().name
    app ='' 
    if sname!='MainProcess':
	app=sname.split('-')[1]
        ts = 0.2*(1+random())
        if app=='1':
            ts=0.1
        sleep(ts)
        i += 1
        print '\r '+str(i),
        #print "%r a fini une tache %r"%(app,ts)

    return str(data * 2) + ':' + app

def run_script(command = None):
    """
    This function is intended to be a "buffer" for sub-processes that will be 
    created
    """
    os.system('python '+command +' -b 243')

def start_process():
    print 'Starting', multiprocessing.current_process().name

def generate_commands():
    """
    Pretty obvious for now but provides cleaner architecture
    """
    commands = ['rep1/fichier.py','rep2/fichier.py','rep3/fichier.py'] * 10
    
    #Pour ne pas avoir a ecrire 30 scripts
    
    return commands
    
    

if __name__ == '__main__':

    pool_size = multiprocessing.cpu_count() * 2
    
    print 'creating %r processes'%pool_size

    pool = multiprocessing.Pool(processes=pool_size)
    
    #pool_outputs = pool.map(do_calculation, inputs)
    pool_out2 = pool.map(run_script, generate_commands())
    pool.close() # no more tasks
    pool.join()  # wrap up current tasks
 
