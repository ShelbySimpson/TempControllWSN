#! /bin/python2
import serial
import sys
import time as tm
from time import sleep
import time as tm
import os
import signal
import string
from datetime import datetime, time, timedelta
import baseStationHelper as bsh

#explain command line inputs
def usage():
  print( "usage: /base.py serial_port wakeUpTime desired_temp")
  print( "    serial_port   = 'COMX' | '/dev/tty.usbXXXX'")
  print("    Wake up time, military  = '14:02'")
  print("    Desired Temperature = 'int'")
 
sigHand = True;#signal Handler

data = [];#list to store sensor data
baud = 9600;


#clean up tasks before program exits
def signal_handler(signal, frame):
    #empty out whats left in serial and save to data list
    while ser.inWaiting(): 
        sData = ser.readline().strip();
        data.append(sData);
        sys.stdout.flush()

    #create a timestamp name for file
    sensorDataName = tm.strftime("%m_%d_%y_%H_%M",tm.localtime());
    #add rate sensor details to filename
    sensorDataName = sensorDataName + ".csv";
    #write data list to file,close file
    sensorDataFile = open(sensorDataName,'w');
    #write data to file
    print("Writing data to file...");
    for item in data:
        #item = str(item,'utf-8');#convert from bytes to String
        sensorDataFile.write(item + '\n');#add newline
        print(item);#allow user to see what has being written to file.
    sensorDataFile.close();
    print("Done writing data");
    
    sigHand = False
    #notify arduino that program is done writing, exit
    ser.write(b'T')
    ser.close()
    os._exit(0)

#init signal, waits for keyboard interrupt(Ctrl-Z)
signal.signal(signal.SIGINT, signal_handler)

#command line validataion==================================
#check num arguments
if len(sys.argv) != 4:
    usage()#not enough, inform user
    os._exit(1)#exit program
else:
    serial_port = sys.argv[1];#save serial port

try:
    dsrTemp = int(sys.argv[3])
    print("this is dsrtemp: ",dsrTemp)
except:
    usage()
    os._exit(1)
#check that timp param is in correct format
try:
    srtTime = bsh.getStartUpTime(sys.argv[2])

except:
    usage();
    os._exit(1)#exit program
#===========================================================

try:
    power = False
    finished = False 
    waiting = True
    thresholdRelevant = False
    lightThreshold = 500
    darkLimit = 10;#7200 limit in seconds, which is 2hrs
    darkTime = tm.time();
    print("Now: " ,datetime.now())
    #create connection with port
    ser = serial.Serial(serial_port, baud, timeout=1);
    sleep(1);#allow time to create serial object
    #turn off power
    ser.write(b'F')
    #now = datetime.now()
    #now_time = now.time()
    while not finished:
        #"Sleeping"************************************************************************
        if waiting:
            now = datetime.now()
            now_time = now.time()
            print("waiting until: ",srtTime,"current time: ",now_time)
        #Wakeup actions*********************************************************************
        #check to see if it is wakeup time
        if now_time.strftime('%H:%M') == srtTime.strftime('%H:%M') and waiting == True:
                #WarmUp time, setup system
                waiting = False
                #activate sampling from heater node
                initData = 'X'#X is being used only for demo purposes. R is normal start
                initData = initData.encode('utf-8');#encode data,bytes for serial port
                ser.write(initData);#write data collection has been initialized
                sleep(.5)
                #get inital readings
                if ser.inWaiting() > 0:
                    #read in line and strip \r\n, for csv formatting purposes
                    #newline is added when written to file.
                    sData = ser.readline().strip();
                    sData = str(sData,'utf-8')
                    timeStampData = sData + "," + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data.append(timeStampData);

                    #seperate data for analysis
                    sData = sData.split(",")
                    light = int(sData[1])
                    temp = int(sData[2])

                    if light < lightThreshold:
                        darkTime = tm.time() 
                    print(timeStampData);#let user see data

        if not waiting:
            if ser.inWaiting() > 0:
                #read in line and strip \r\n, for csv formatting purposes
                #newline is added when written to file.
                sData = ser.readline().strip();
                sData = str(sData,'utf-8')
                timeStampData = sData + "," + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data.append(timeStampData);

                #seperate data for analysis
                sData = sData.split(",")
                light = int(sData[1])
                temp = int(sData[2])

                if(light > lightThreshold):
                    print ("this is light: ",light)
                    print("thresholdRelevant = false")
                    print("1st temp: " , temp)
                    thresholdRelevant = False
                elif light < lightThreshold and not thresholdRelevant:
                    print("thresholdRelevant = True")
                    print("2nd Temp: " , temp)
                    thresholdRelevant = True
                    darkTime = tm.time()
                elif light < lightThreshold and thresholdRelevant:
                    print("this is darkTime", tm.time() - darkTime)
                    print ("this is light: ",light)
                    print("thresholdRelevantt = True")
                    print("third temp: ", temp)
                    passedTime = tm.time() - darkTime
                    print("This is passedTime: ",passedTime)
                    if(tm.time() - darkTime) > darkLimit:
                        thresholdRelevant = False
                        waiting = True
                        #send message to have heater node quit sampling
                        ser.write(b'T')
                        #turn off power
                        ser.write(b'F')
        if not waiting:
            if temp >= (dsrTemp + 2):
                if power:
                    print("Power off! Temp: ", temp)
                    power = False
                    ser.write(b'F')
            elif temp <= (dsrTemp - 2):
                if not power:
                    print("Power On! Temp: ", temp)
                    power = True
                    ser.write(b'O')
                #===========================================================================
except:
    print( "unexpected error:", sys.exc_info());



