import os
from time import sleep
from random import random
s=4*(1+random())
somme=0
for i in range(1,10000*int(s)):
    somme += 1/float(i)
    
print "%r demarre s= %r"%(os.getpid(),s)
sleep(0.1)
print "%r a fini"%os.getpid()
