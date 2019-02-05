# Compile the python file encrypted 

import os
import sys
from subprocess import call

if len(sys.argv) < 3:
    print('Please specify the path and your module name!')
    exit(1)

path = sys.argv[1]
prog_name = sys.argv[2]
my_name = sys.argv[0]

print my_name

pwd = os.getcwd()
files = os.listdir('.')
compile_files = {}

# enum python file in the current path
for i in files:
    if i.endswith('.py'):
        compile_files[i.split('.')[0]] = i

try:
    import Cython
except ImportError, e:
    print "Cython is not installed. Maybe you need $ pip install cython"
    exit(2)

# write compile.py as Makefile for cython
with open(pwd + '/' + '_compile.py', 'w') as fw:
    fw.write('from distutils.core import setup\n')
    fw.write('from distutils.extension import Extension\n')
    fw.write('from Cython.Distutils import build_ext\n')
    fw.write('\n')
    fw.write('ext_modules = [\n')
    for k, v in compile_files.items():
        if v != my_name:
            fw.write('\tExtension(\"%s\", [\"%s\"]),\n' % (k, v))
    fw.seek(-2, os.SEEK_END)
    fw.write('\n]\n')
    fw.write('\n')
    fw.write('setup(\n')
    fw.write('\tname = \'%s\',\n' % prog_name)
    fw.write('\tcmdclass = {\'build_ext\': build_ext},\n')
    fw.write('\text_modules = ext_modules\n')
    fw.write(')\n')





