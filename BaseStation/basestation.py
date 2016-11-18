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

def getData(signal, frame):
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

#read in data and write to list data structure
def handleSensorData(ser):
    #while user hasn't interrupted data collection process 
    #save data to list
    while sigHand:
        while ser.inWaiting(): 
            #read in line and strip \r\n, for csv formatting purposes
            #newline is added when written to file.
            sData = ser.readline().strip()
            sData = str(sData,'utf-8')
            timeStampData = sData + "," + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data.append(timeStampData);
            print(timeStampData);#let user see data 
            #seperate data for analysis
            #item = str(sData,'utf-8');#convert from bytes to String
            #sData = item.split(",")
            #time = sData[0]
            #light = sData[1]
            #temp = sData[2]
            sleep(.5);#allow time to handle data before reading again
            sys.stdout.flush();#flush
    

#init signal, waits for keyboard interrupt(Ctrl-Z)
signal.signal(signal.SIGINT, signal_handler)

def getLightTemp(ser):
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
    lightThreshold = 400
    #darkLimit = time(2,00)#limit in hours to how long the light can be below threshold
    darkLimit = 7200;#limit in seconds, which is 2hrs
    print("Now: " ,datetime.now())
    #create connection with port
    ser = serial.Serial(serial_port, baud, timeout=1);
    sleep(1);#allow time to create serial object
    now = datetime.now()
    now_time = now.time()
    while not finished:
        #"Sleeping"************************************************************************
        if waiting:
            print("waiting until: ",srtTime,"current time: ",now_time)
            now = datetime.now()
            now_time = now.time()
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
                        darkCounter = tm.time() 
                        print("this is darkcounter: " , darkCounter)
                    print(timeStampData);#let user see data

        if not waiting:
            now = datetime.now()
            now_time = now.time()
            currTime = now_time.strftime('%H:%M')
            if light < lightThreshold:
                #check to see darkLimit time has expired
                elapsedTime = now - darkCounter


            if temp >= (dsrTemp + 2):
                power = False
            elif temp <= (dsrTemp - 2):
                power = True
                #===========================================================================
                #Heater will turn on if temp is below desired temp
                #if need_heat(temp,dsrTemp):
                    #finished = True
        #while ser.inWaiting()
            #handleSensorData(ser);#handle incoming data
    #os.exit(0);

except:
    print( "unexpected error:", sys.exc_info());



