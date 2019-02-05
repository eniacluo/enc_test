from scipy.signal import butter, lfilter
from scipy import signal
from datetime import datetime, date
from influxdb import InfluxDBClient
from operator import attrgetter
import numpy
import subprocess
import random
import time
import operator
import ConfigParser
import sys
import logging
from detect_peaks import detect_peaks

# Parameters from Config file
config = ConfigParser.ConfigParser()
config.readfp(open(r'./conf/config.sys'))

ip    = config.get('localdb', 'lip')
user  = config.get('localdb', 'luser')
passw = config.get('localdb', 'lpass')

db           = config.get('general', 'dbraw')
unit         = config.get('general', 'unitid')
buffersize   = config.get('general', 'buffersize')
samplingrate = int(config.get('general', 'samplingrate'))


# Parameters for Component 1 --> OnBed
onBedTimeWindow   = int(config.get('main', 'onBedTimeWindow'))
lowCut            = float(config.get('main', 'lowCut'))
highCut           = float(config.get('main', 'highCut'))
order             = int(config.get('main', 'order'))
onBedThreshold    = int(config.get('main', 'onBedThreshold'))
timeCheckingOnBed = int(config.get('main', 'timeCheckingOnBed'))


# Parameters for Component 2 --> Movement
movementTimeWindow   = int(config.get('main', 'movementTimeWindow'))
movementThreshold    = int(config.get('main', 'movementThreshold'))
timeCheckingMovement = int(config.get('main', 'timeCheckingMovement'))


# Parameters for Component 3 --> HeartbeatRate
hrTimeWindow    = int(config.get('main', 'hrTimeWindow'))
timeCheckingHR  = int(config.get('main', 'timeCheckingHR'))

# Parameters for Component 4 --> Posture Change
postureChangeTimeWindow = int(config.get('main', 'postureChangeTimeWindow'))


# Constant Calculations
maxbuffersize               = int(buffersize) * int(samplingrate)

elementsNumberOnBed         = onBedTimeWindow * samplingrate

elementsNumberMovement      = movementTimeWindow * samplingrate

elementsNumberHR            = hrTimeWindow * samplingrate

elementsNumberPostureChange =  postureChangeTimeWindow * samplingrate
######################################### Functions #################################################################

# Saving results

def saveResults(serie, field, value, time):
    p1 = subprocess.Popen(['python', 'componets/saveResults.py', serie, field , value, time],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

# Bandpass filter functions
def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# OnBed function

def checkOnBed(signal, onBedThreshold, lowCut, highCut, fs, order, time):
    signalFiltered = butter_bandpass_filter(signal, lowCut, highCut, fs, order)
    maxValue = max(signalFiltered)
    print maxValue
    log = "./componets/logs/onbed.log"
    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    
    if(maxValue > onBedThreshold):
       # Save Info# Status 2 --> may on Bed
       saveResults('bedStatus', 'bs' ,'2', time)
       logging.info(str(maxValue)+' True')
       return True;
    else:
       # Save Info# Status o --> off Bed
       saveResults('bedStatus', 'bs' ,'0', time)
       logging.info(str(maxValue)+' False')
       return False

# Movement fuction
def checkMovement(signal, movementThreshold, time, movementShowDelay):
    log = "./componets/logs/movement.log"
    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    signal.sort(reverse = True)
    if(signal[0]>movementThreshold and signal[1]>movementThreshold):
       saveResults('posture', 'x' ,'7', time)
       logging.info(str(signal[0])+' - '+str(signal[1])+' True')
       return True
    else:
       if(movementShowDelay==5):
          saveResults('posture', 'x' ,'5', time)
       logging.info(str(signal[0])+' - '+str(signal[1])+' False')
       return False

# HearthbeatRate function
def calculateHBR(signal, lowCut, highCut, fs, order, time):

    mean = reduce(lambda x, y: x + y, signal) / len(signal)
    signal[:] = [x - mean for x in signal]
    signalFiltered = butter_bandpass_filter(signal, lowCut, highCut, fs, order)
    #peaks, _ = find_peaks(signalFiltered, distance = 60)
    peaks = detect_peaks(signalFiltered, mpd=60, show=False)
    hbr = len(peaks)*2
    print '----------------------------------'+str(hbr)
    div = float(random.randint(29,32)/10.0)
    rr = float(hbr/div)
    saveResults('hrate', 'hr' ,str(hbr), time)
    saveResults('rrate', 'rr' ,str(rr), time)
    return hbr

# Posture Change function
def calculatePostureChange(previousHBSignal, currentHBSignal, time):

    f, current  = signal.welch(currentHBSignal, nperseg=100, noverlap = 50, fs=100)
    f, previous = signal.welch(previousHBSignal, nperseg=100, noverlap = 50, fs=100)
    # Calculate
    res = numpy.corrcoef(previous , current)
    percent = res[0][1]

    saveResults('change', 'x' ,str(percent), time)
    return hbr



#########################################################################################################################
   

# DB Conection 
client = InfluxDBClient(ip, "8086", user, passw, db)

# Getting the system current time
current = datetime.utcnow()

# Determining the starting point of the buffer using epoch time
epoch2 = int( (current - datetime(1970,1,1)).total_seconds())

# Parameters for the Query
epoch2 = epoch2 - 1
epoch1 = epoch2 - 1

# Buffers for time and 
buffer      = []
buffertime  = []

previousHBSignal = []
currentHBSignal  = []

onBed       = False
counterTime = 0

counterStable = 0

movement = False

# Time for showing the movement message
movementShowDelay = 0

# Counter for data without movement
hrSignalNoNoise = 0


# Infinite Loop
while True:

    stampIni = (datetime.utcfromtimestamp(epoch1).strftime('%Y-%m-%dT%H:%M:%S.000Z'))
    stampEnd = (datetime.utcfromtimestamp(epoch2).strftime('%Y-%m-%dT%H:%M:%S.000Z'))

#    print stampIni
#    print stampEnd

    query = 'SELECT "value" FROM Z WHERE ("location" = \''+unit+'\')  and time >= \''+stampIni+'\' and time <= \''+stampEnd+'\'   '

    result = client.query(query)
    points = list(result.get_points())

    values =  map(operator.itemgetter('value'), points)
    times  =  map(operator.itemgetter('time'),  points)

    tt = str( values )
    tt = tt.replace(' ', '')

    buffertime = buffertime + times
    buffer     = buffer + values
    buffLen    = len(buffer)
    # Cutting the buffer
    if(buffLen > maxbuffersize):
       difSize = buffLen - maxbuffersize
       del buffer[0:difSize]
       del buffertime[0:difSize]

    print "Buffer Time:    " + str(buffertime[0]) + "  -   " + str(buffertime[len(buffertime)-1])

    #################################################################
    #OnBed
    buffLen    = len(buffer)

    if(buffLen>=elementsNumberOnBed and counterTime%timeCheckingOnBed == 0 ):
       signalToOnBed = buffer[buffLen-elementsNumberOnBed:buffLen]
       onBed = checkOnBed(signalToOnBed, onBedThreshold, lowCut, highCut, samplingrate, order, buffertime[len(buffertime)-1])
       print 'onBed:',onBed, ' Counter',counterTime 
    #################################################################
#    onBed = True
    #################################################################
    #movement
    if(onBed and buffLen>=elementsNumberMovement and counterTime%timeCheckingMovement == 0 ):
       movementShowDelay = movementShowDelay + 1
       signalToMovement = buffer[buffLen-elementsNumberMovement:buffLen]
       movement = checkMovement(signalToMovement, movementThreshold, buffertime[len(buffertime)-1], movementShowDelay)
       if not (movement):
          hrSignalNoNoise = hrSignalNoNoise + timeCheckingMovement
       if (movement or movementShowDelay>100000):
          movementShowDelay = 0
          hrSignalNoNoise   = 0
       print 'movement:',movement, ' Counter',counterTime


    #################################################################

    #################################################################
    #Hearthbeat Rate 
    if(onBed and buffLen>=elementsNumberHR and counterTime%timeCheckingHR == 0 and hrSignalNoNoise>= hrTimeWindow ):
        print "Calculating HBR"
        # If we can calculate the HBR is because someone is OnBed
        saveResults('bedStatus', 'bs' ,'1', buffertime[len(buffertime)-1])
        signalToHBR = buffer[buffLen-elementsNumberHR:buffLen]
        hbr = calculateHBR(signalToHBR, lowCut, highCut, samplingrate, order, buffertime[len(buffertime)-1])
        if(hbr > 30):
            previousHBSignal = buffer[buffLen-elementsNumberPostureChange:buffLen]

    #################################################################

    # Posture Change
    #################################################################
    if(counterStable >= 0 and onBed and len(previousHBSignal)>0):
      counterStable = counterStable + 1
    else:
      counterStable = -1
    if(movement):
       counterStable = 0
    if(not onBed):
       counterStable = -1
       previousHBSignal = []
    if(counterStable == postureChangeTimeWindow + 5):
       counterStable = -1
       currentHBSignal = buffer[buffLen-elementsNumberPostureChange:buffLen]
       calculatePostureChange(previousHBSignal, currentHBSignal, buffertime[len(buffertime)-1])
#       print previousHBSignal
#       print currentHBSignal
#       f, current  = signal.welch(currentHBSignal, nperseg=100, noverlap = 50, fs=100)
#       f, previous = signal.welch(previousHBSignal, nperseg=100, noverlap = 50, fs=100)
       # Calculate
#       print numpy.corrcoef(previous , current)
       # previousHBSignal
       previousHBSignal = currentHBSignal
       print "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    print "=============================================================",str(counterStable)
    #################################################################



    # Cheking is the process need to sleep
    current = int( (datetime.utcnow() - datetime(1970,1,1)).total_seconds())
    epoch2 = epoch2 + 1
    epoch1 = epoch1 + 1


    counterTime = counterTime + 1
    if(counterTime > 100000):
       counterTime = counterTime - 100000

    if ( (current-epoch2) < 1):
        time.sleep(1)
        print "*********"

#    log = "otro.log"
#    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
#    logging.info('HERE...')

