import multiprocessing
from time import sleep
from pprint import pprint
import pdb
from random import random 
import os
from StringIO import StringIO
import sys

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

def run_script(script=None ,sio=None):
    """
    This function is intended to be a "buffer" for sub-processes that will be 
    created
    """
    os.system('python '+script +' -b 243')
    
    if sio:
        sio.write(multiprocessing.current_process().name + ("-"*12) 
                  +str(os.getpid()))
        sio.flush()
        sio.seek(0)
        print(sio.read())
        sio.seek(0)

def start_process():
    print 'Starting', multiprocessing.current_process().name

def generate_scripts_names():
    """
    Pretty obvious for now but provides cleaner architecture
    """
    scripts = ['rep1/fichier.py','rep2/fichier.py','rep3/fichier.py'] * 4
    
    #Pour ne pas avoir a ecrire $n$ scripts
    
    return scripts
    
def generateStringIOs(list_or_int=1):
    t = type(list_or_int)
    if t == type([]) or t==type(()):
        l=len(list_or_int)
    elif type(list_or_int)==type(0):
        l=list_or_int
    #Il doit y avoir plus elegant/pythonique ...
    else:
        raise(TypeError)
    #Comment mettre un message ?

    res=[]
    for i in range(l):
        res.append(StringIO())
    return res
            
if __name__ == '__main__':

    pool_size = multiprocessing.cpu_count() * 2
    scripts = generate_scripts_names()
    sios=generateStringIOs(scripts)
    print 'creating %r processes'%pool_size
    
    pool = multiprocessing.Pool(processes=pool_size)
    
    #pool_outputs = pool.map(do_calculation, inputs)
    new_inputs=[]
    #import pdb;pdb.set_trace()
    """
    for i in range(len(scripts)):
        x=scripts[i]
        y=sios[i]
        y.write('test')
        e=[x,y]
        new_inputs.append(e)
    """
    newer_inputs=[]
    for i in range(len(scripts)):
        newer_inputs.append({'script':scripts[i],'sio':sios[i]})

    
    p_list=[]
    for a in newer_inputs:
        p_list.append(multiprocessing.Process(target=run_script ,kwargs=a))
        
    for p  in p_list:
        p.start()
        p.join()
    """
    Can't see a straightforward option unless recoding some pool features
    so as to launch n processes and when one og them is done launching a new 
    on using a lock between provder anec consumer ...

    """
    #not sure about arguments handling,thus i tried with this list
    #pool_out2 = pool.map(run_script,newer_inputs)
    #pool.close()
    #pool.join()
 
    
  
    #import pdb;pdb.set_trace()
    """
    for s in sios:
        s.seek(0)
        print(s.read())
    """
    sys.stdout.flush()
