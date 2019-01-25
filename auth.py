#!/usr/bin/python2.7

import subprocess
import sys

if sys.argc < 2:
    print "file compiled needed."
    exit(1)
    
serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | awk \'{print($3)}\'', shell=True)[:-1]

cmp_serial = subprocess.check_output('openssl enc -d -a -aes-256-cbc -pass pass:sensorweb987 -in key', shell=True).split('\n')[0]

if serial == cmp_serial:
    import _main ### <-- this is the entry point of our code
    pass
else:
    print 'Permission denied.'
