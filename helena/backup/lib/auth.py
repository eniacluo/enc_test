#!/usr/bin/python2.7

import subprocess
import sys

if len(sys.argv) < 2:
    print "password needed."
    exit(1)
    
serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | awk \'{print($3)}\'', shell=True)[:-1]

try:
    cmp_serial = subprocess.check_output('openssl enc -d -a -aes-256-cbc -pass pass:%s -in key' % (sys.argv[1]), shell=True).split('\n')[0]
except:
    print 'Permission denied.'
    exit(0) 

if serial == cmp_serial:
#    try:
    import _main ### <-- this is the entry point of our code
#    except:
#        print 'main module missing.'
    pass
else:
    print 'Permission denied.'
