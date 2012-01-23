import multiprocessing
import os 

from testpool import generate_scripts_names ,generateStringIOs

#some test fo cgoutte

def pooled_task(sio = None, script = None):
    #sio=a['sio']
    #script=a['script']
    print "pt :" + multiprocessing.current_process().name
    if script is not None:
        os.system('python '+script)
    if sio:
        sio.write('Test')
        sio.seek(0)
        print(sio.read())

def tl(a):
    while(not a.empty()):
        x = a.get()
        pooled_task(**x)
        

if __name__ == '__main__':
    Q1=multiprocessing.Queue()
    sn=generate_scripts_names()
    sn *= 5
    sios = generateStringIOs(sn)
    nb=12
    ll = len(sn)
    ll = range(ll)
    for x in ll:
        Q1.put({'sio':sios[x],'script':sn[x]})
    

    p_list=[]
    for x in range(nb):
        p_list.append(multiprocessing.Process(target = tl,args = (Q1,)))
    for p in p_list:
        p.start()

    for p in p_list:
        p.join()
        
    print 'joined !! '
    
    for x in sios:
        x.seek(0)
        print(x.read())




