# argv[1]: the entry point python module

mv $1 _main.py

python gen_makefile.py . $1

if [ -e _compile.py ]
then
    python _compile.py build_ext --inplace
    rm _compile.py
fi

cython --embed -o auth.c auth.py 
output=$(echo $1 | cut -f 1 -d '.')
arm-linux-gnueabihf-gcc -Os -I /usr/local/include/arm-linux-gnueabihf/python2.7/ -o $output auth.c -lpython2.7 -lpthread -lm -lutil -ldl

mv _main.py $1