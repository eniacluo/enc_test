# argv[1]: the entry point python module

mv $1 _main.py
mv auth.py $1

#python gen_makefile.py . $1

#if [ -e _compile.py ]
#then
#    python _compile.py build_ext --inplace
#    rm _compile.py
#fi

#cython --embed -o auth.c auth.py
#output=$(echo $1 | cut -f 1 -d '.')
#gcc -Os -I /usr/include/python2.7/ -o $output auth.c -lpython2.7 -lpthread -lm -lutil -ldl

pyinstaller --hidden-import influxdb $1

mv $1 auth.py
mv _main.py $1
#rm -r build *.c auth.so

#mkdir build
#mv *.so $output build/
