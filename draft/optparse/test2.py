import multiprocessing
import os 

from testpool import generate_scripts_names ,generateStringIOs

def pooled_task(sio=None,script=None):
    #sio=a['sio']
    #script=a['script']
    print "pt :"+ multiprocessing.current_process().name
    if script is not None:
        os.system('python '+script)
    if sio:
        sio.write('Test')
        sio.seek(0)
        print(sio.read())

def tl(a):
    while(not a.empty()):
        x=a.get()
        pooled_task(**x)
        

if __name__=='__main__':
    Q1=multiprocessing.Queue()
    sn=generate_scripts_names()
    sn *= 5
    sios=generateStringIOs(sn)
    nb=12
    ll=len(sn)
    ll=range(ll)
    for x in ll:
        Q1.put({'sio':sios[x],'script':sn[x]})
    
    #import pdb;pdb.set_trace()
    for x in range(nb):
        multiprocessing.Process(target=tl,args=(Q1,)).start()
    
        




