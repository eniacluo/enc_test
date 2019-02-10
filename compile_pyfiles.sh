# argv[1]: the entry point python module

if [ ! $# -eq 1 ]
then
    echo 'entry point module name (.py) is required!'
    exit
fi

# set auth.py as the entry point of programs
# _main.py is entry point what user specified

mv $1 _main.py
mv auth.py $1

pyinstaller --onefile $1 --log-level DEBUG --key=@@@SensorWeb0987 # this key is for encrypting the bytecode

mv $1 auth.py
mv _main.py $1
