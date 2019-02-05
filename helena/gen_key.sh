cat /proc/cpuinfo | grep Serial | awk '{print($3)}' > temp
echo "SIMONDIDTHIS" >> temp

openssl enc -a -e -salt -aes-256-cbc -pass pass:$1 -in temp -out temp.enc

mv temp.enc key
rm temp
