#! /bin/python2
import serial
import time
import sys
from time import sleep
import os
import signal
import string
import datetime
import baseStationHelper as bsh

#explain command line inputs
def usage():
  print( "usage: /base.py serial_port sensor rate")
  print( "    serial_port   = 'COMX' | '/dev/tty.usbXXXX'")
 
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
    sensorDataName = time.strftime("%m_%d_%y_%H_%M",time.localtime());
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
            sData = ser.readline().strip();
            sData = str(sData,'utf-8')
            timeStamp = sData + "," + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data.append(timeStamp);
            print(timeStamp);#let user see data 
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
try:
    #check num arguments
    if len(sys.argv) != 2:
        usage()#not enough, inform user
        os._exit(1)#exit program
    else:
        serial_port = sys.argv[1];#save serial port
    #bsh.getStartUpTime("19:21")
    
    #create connection with port
    ser = serial.Serial(serial_port, baud, timeout=1);
    sleep(2);#allow time to create serial object

    initData = 'R'
    initData = initData.encode('utf-8');#encode data,bytes for serial port
    ser.write(initData);#write data collection has been initialized
    print("Now: " , datetime.datetime.now())
    handleSensorData(ser);#handle incoming data
    os.exit(0);

except:
    print( "unexpected error:", sys.exc_info());



