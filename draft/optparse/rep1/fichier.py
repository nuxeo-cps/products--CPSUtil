import os
from time import sleep
from random import random
from optparse import OptionParser

p=OptionParser()
p.add_option('-b',dest='taille')
opt,args=p.parse_args()



s=4*(1+random())

if opt.taille:
    print 'option passee : %r'%opt.taille



somme=0
for i in range(1,500000*int(s)):
    somme += 1/float(i)
    
print "%r demarre s= %r"%(os.getpid(),s)
sleep(0.1)
print "%r a fini"%os.getpid()
print __name__

