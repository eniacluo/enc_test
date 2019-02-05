from influxdb import InfluxDBClient
import numpy as np
import argparse
import time

def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='example code to play with InfluxDB')
    parser.add_argument('--host', type=str, required=False, default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--user', type=str, required=False, default='Jose',
                        help='InfluxDB user name')
    parser.add_argument('--passw', type=str, required=False, default='sensorweb',
                        help='InfluxDB password')
    parser.add_argument('--dbname', type=str, required=False, default='shake',
                        help='Data Base Name')
    parser.add_argument('--table', type=str, required=False, default='Z',
                        help='table ex. Z')
    parser.add_argument('--filterr', type=str, required=False, default='',
                        help='Unit Name eg. R6')
    parser.add_argument('--fromt', type=str, required=False, default='0',
                        help='Start Time')
    parser.add_argument('--to', type=str, required=False, default='0',
                        help='End Time')

    return parser.parse_args()

def startTime(host, user, passw, dbname, table, filterr, port):
    if(len(filterr)): 
        query = 'SELECT "value" FROM "'+table+'" WHERE ("location" = \''+filterr+'\') AND time >= now() - 1m ORDER BY time DESC'
    else:
        query = 'SELECT "value" FROM "'+table+'" WHERE time >= now() - 1m ORDER BY time DESC'
  
    client = InfluxDBClient(host, port, user, passw, dbname)

    result = client.query(query)
    points = list(result.get_points())
        

    aList = [];

    stamp = "";
    count = 0      
    for point in points:
        stamp = point['time']
        break;

    return stamp;



def main(host, user, passw, dbname, table, filterr, fromt, to):
    debug=0
    if(debug==1): 
        print host 
        print user 
        print passw 
        print dbname 
        print table 
        print filterr 
        print fromt 
        print to

    port  = 8086
    stamp = startTime(host, user, passw, dbname, table, filterr, port)
    print stamp


    while (1):
        time.sleep( 5 )

        if(len(filterr)): 
            query = 'SELECT "value" FROM "'+table+'" WHERE ("location" = \''+filterr+'\') AND time >= \''+stamp+'\' '
        else:
            query = 'SELECT "value" FROM "'+table+'" WHERE time >= \''+stamp+'\' '

        client = InfluxDBClient(host, port, user, passw, dbname)

        result = client.query(query)
        points = list(result.get_points())
        
        aList = [];

        count = 0      
        for point in points:
            aList.append( point['value'] );
            stamp = point['time']
            count = count +1

#      print aList #The data are here!!!
        print stamp

#          Here your code


args = parse_args()
main(host=args.host, user=args.user, passw=args.passw, dbname=args.dbname, table=args.table, filterr=args.filterr, fromt=args.fromt, to=args.to)


