import socket as s
from decimal import Decimal
import subprocess
import ConfigParser


# Parameter from configuation File
config = ConfigParser.ConfigParser()
config.readfp(open(r'../conf/config.sys'))

ip    = config.get('localdb', 'lip')
user  = config.get('localdb', 'luser')
passw = config.get('localdb', 'lpass')

print ip
rip    = config.get('remotedb', 'rip')
ruser  = config.get('remotedb', 'ruser')
rpassw = config.get('remotedb', 'rpass')

db    = config.get('general', 'dbraw')
unit  = config.get('general', 'unitid')

port = 8888								# Port to bind to
hostipF = "/opt/settings/sys/ip.txt"
file = open(hostipF, 'r')
host = file.read().strip()
file.close()

HP = host + ":" + str(port)
print "  Opening socket on (HOST:PORT)", HP

sock = s.socket(s.AF_INET, s.SOCK_DGRAM | s.SO_REUSEADDR)
sock.bind((host, port))

print "Waiting for data on (HOST:PORT) ", HP

while 1:								# loop forever
    data, addr = sock.recvfrom(1024)	# wait to receive data
#    print data
    data = data.replace("}", "")
    data2 = data.split(",")							
    timestampi =  Decimal(data2[1])
    timeIni = timestampi * 1000
    count = 0;
    http_post  = "curl -i -XPOST \'http://"+ ip+":8086/write?db="+db+"\' -u "+ user+":"+ passw+" --data-binary \' "
#    http_post2 = "curl -i -XPOST \'http://"+rip+":8086/write?db="+db+"\' -u "+ruser+":"+rpassw+" --data-binary \' "

    for f in data2:
       count  = count + 1
       if(count>2):    
#          print int(f)
#          print timeIni
          http_post  += "\nZ,location="+unit+" value=" 
          http_post  += str(int(f)) + " " + str(int(timeIni*1000000))
        
#          http_post2 += "\nZ,location="+unit+" value="
#          http_post2 += str(int(f)) + " " + str(int(timeIni*1000000))

          timeIni = timeIni + 10
    
    http_post += "\'  &"
#    http_post2 += "\'  &"
    
#    print http_post2
    subprocess.call(http_post, shell=True)
#    subprocess.call(http_post2, shell=True)

