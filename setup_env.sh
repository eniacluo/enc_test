pip install pyinstaller

if [ ! $# -eq 1 ]
then
    echo "the path of storing files to compile is required!"
    exit
fi

cp compile_pyfiles.sh auth.py gen_key.sh "$1"

echo ""
echo "use 'compile_pyfiles.sh <main python file name>' to compile."
echo ""
