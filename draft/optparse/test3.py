import os 
import subprocess
import multiprocessing
import shlex
from time import clock
from testpool import generate_scripts_names ,generateStringIOs

#Merging with gracinet's idea

"""
This scripts aims to provide 
Parrallel processing of CPS test.
As they may take la long time to run we try to profile them as they take long to execute.

"""

class scriptObject():
    def __init__(self,script = '' , cmd = 'python' , options = ''):
        self.script = script
        self.cmd = cmd
        self.options = options
    
    def system_instr(self):
        return shlex.split(' '.join([self.cmd,self.script,self.options]))
        return [self.cmd , self.script,self.options]

    def __str__(self):
        return self.__dict__.__str__()
    

def do_thing(scr_obj = None):
    
    """
    Wrap for pooling and launching processes
    Here try to monitor time taken since real tasks may take quite a long time 
    to complete. Then they the longest test should be lauch first so as to avoid
    having to wait for them to complete
    a good thing would be to pickle results (in the future) for now i'll juste try to 
    have them computed
    """
    res = {}

    t1 = clock()
    if not scr_obj:
        return "No task provided"
    ags = scr_obj.system_instr()
    
    son = subprocess.Popen(ags)
    print "spid %r pid %r "%(son.pid,os.getpid())
    if os.waitpid(son.pid,0):
        print times()
        res['duration'] = clock()-t1
    return res

if __name__ == '__main__':

    scripts = [scriptObject(x, options = '-b 4') for x in generate_scripts_names()]
    print('the following commands will be executed')
    for x in scripts:
        print x.system_instr()

    p = multiprocessing.Pool(processes = 1)
    resultat = p.map(do_thing, scripts)

    for x in resultat:
        print x['duration']
