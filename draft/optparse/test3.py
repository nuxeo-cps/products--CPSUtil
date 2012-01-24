import os 
import multiprocessing
from time import clock
from testpool import generate_scripts_names ,generateStringIOs

#Merging with gracinet's idea

class scriptObject():
    def __init__(self,script = '' , cmd = 'python' , options = ''):
        self.script = script
        self.cmd = cmd
        self.options = options
    
    def system_instr(self):
        return ' '.join([self.cmd,self.script,self.options])

    def __str__(self):
        return self.__dict__.__str__()
    

def do_thing(scr_obj = None):
    res={}
    t1=clock()
    if not scr_obj:
        return "No task provided"
    os.system( scr_obj.system_instr() )
    print os.getpid()
    
    res['duration']=clock()-t1
    
    return res

if __name__ == '__main__':

    scripts = [scriptObject(x, options = '-b 4') for x in generate_scripts_names()]
    print('the following commands will be executed')
    for x in scripts:
        print x.system_instr()

    p = multiprocessing.Pool(processes = 2)
    resultat = p.map(do_thing, scripts, 1)

    for x in resultat:
        print x['duration']
