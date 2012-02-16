import multiprocessing
import os 
from time import time,clock
from testpool import generate_scripts_names ,generateStringIOs

#some test fo cgoutte

def pooled_task(sio = None, script = None):
    #sio=a['sio']
    #script=a['script']
    print "pt :" + multiprocessing.current_process().name
    if script is not None:
        os.system('python '+script);
    if sio:
        sio.write('Test')
        sio.seek(0)
        print(sio.read())

def tl(a):
    while(not a.empty()):
        t1=time()
        x = a.get()
        pooled_task(**x)
        t2=time()
        print "%r "%(t2-t1)

if __name__ == '__main__':
    clock()
    t0=time()
    Q1=multiprocessing.Queue()
    sn=generate_scripts_names()
    sn *= 5
    sios = generateStringIOs(sn)
    nb=12
    #number of processes,
    ll = len(sn)
    ll = range(ll)
    for x in ll:
        Q1.put({'sio':sios[x],'script':sn[x]})
    #This needs much more comments    
    #Queues are a good way to store tasks and provide processes
    p_list=[]
    for x in range(nb):
        p_list.append(multiprocessing.Process(target = tl,args = (Q1,)))
    #this way all the (nb) processes receive the same argument
    for p in p_list:
        p.start()

    for p in p_list:
        p.join()
        
    print 'joined !! '
    print clock()
    ###for x in sios:
    #    x.seek(0)
    #    print(x.read())




