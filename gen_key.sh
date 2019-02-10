if [ ! $# -eq 1 ]
then
    echo "key not specified.-> set to default: sensorweb987"
    key=sensorweb987
else
    key=$1
fi

cat /proc/cpuinfo | grep Serial | awk '{print($3)}' > temp
echo "--------" >> temp

openssl enc -a -e -salt -aes-256-cbc -pass pass:$1 -in temp -out temp.enc

mv temp.enc key
rm temp

echo "key generated successful!"
