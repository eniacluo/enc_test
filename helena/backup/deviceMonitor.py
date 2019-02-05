#!/usr/bin/env python
import psutil
import subprocess
import ConfigParser
import time
import os

config = ConfigParser.ConfigParser()
config.readfp(open(r'../conf/config.sys'))
ip    = config.get('localdb', 'lip')
user  = config.get('localdb', 'luser')
passw = config.get('localdb', 'lpass')
db    = config.get('general', 'dbstatus')
unit  = config.get('general', 'unitid')
memoryth  = config.get('system', 'memory')
cputh     = config.get('system', 'cpu')

cpu = psutil.cpu_percent(interval=1)
mem = psutil.virtual_memory().percent
diskp= psutil.disk_usage('/').percent
diskt= (psutil.disk_usage('/').used)/1027/1024

http_post = "curl -i -XPOST \'http://"+ip+":8086/write?db="+db+"\' -u "+user+":"+passw+" --data-binary \'";
http_post = http_post + " \n memory,location="+unit+" value=" +str(mem);
http_post = http_post + " \n cpu,location="+unit+" value="+ str(cpu);
http_post = http_post + " \n diskusagepercent,location="+unit+" value=" + str(diskp);
http_post = http_post + " \n diskusedsize,location="+unit+" value="+ str(diskt) + " \'  ";
subprocess.call(http_post, shell=True)

sw    = 1
tries = 0
while sw:
   sw = 0
   tries = tries + 1
   if int(mem) > int(memoryth):
      sw = 1
      mem = psutil.virtual_memory().percent
      print "system for memory"

   if int(cpu) > int(cputh):
      sw = 1
      cpu = psutil.cpu_percent(interval=1)
      print "system for cpu"
   
   if(tries == 2):
     print "RESTARTING"
     os.system("sudo systemctl reboot");
 
   time.sleep (5)
   


