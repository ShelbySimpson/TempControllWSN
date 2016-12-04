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
    #given inital startup time to be W/O light, time in seconds
    allowedWarmUpTime = 20
    isTemp = False #no inital temp reading
    samplingRate = 2 #in seconds, 300secs = 5mins 
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
                #light will likely not be on at start up time. Keep track of time
                #to use with allowedWarmUpTime var
                warmUpStartTime = tm.time()
                #take care of init setup-----------------------------------------------
                waiting = False
                #activate sampling from heater node
                initData = 'X'#X is being used only for demo purposes. R is normal start
                initData = initData.encode('utf-8');#encode data,bytes for serial port
                ser.write(initData);#write data collection has been initialized
                sleep(.5)
                #----------------------------------------------------------------------
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
                    isTemp = True #let system know that temp has been recieved

                    if light < lightThreshold:
                        darkTime = tm.time() 
                    print(timeStampData);#let user see data

        if not waiting:
            #check to see that node is still sending data
            if ser.inWaiting() == 0:
                sleep(samplingRate)
                if ser.inWaiting() == 0:
                    print("Temp Light Node is no longer Transmitting Data")
                    isTemp = False
                    #turn off power, no response from light temp node
                    ser.write(b'F')
                    #itry to activate sampling from heater node
                    initData = 'X'#X is being used only for demo purposes. R is normal start
                    initData = initData.encode('utf-8');#encode data,bytes for serial port
                    ser.write(initData);#write data collection has been initialized
                    sleep(1)
            if ser.inWaiting() > 0:
                #read in line and strip \r\n, for csv formatting purposes
                #newline is added when written to file.
                sData = ser.readline().strip();
                sData = str(sData,'utf-8')
                timeStampData = sData + "," + datetime.now().strftime("%H:%M")
                data.append(timeStampData);

                #seperate data for analysis
                sData = sData.split(",")
                light = int(sData[1])
                temp = int(sData[2])
                
                isTemp = True
                #==============Light Level Code====================================
                #level of light determines state of power switch
                #if light dips below threshold for given amount of time power is
                #switched off.
                if(light > lightThreshold):
                    thresholdRelevant = False
                    print("======light > lightThreshold======")
                    print("Desired Temp: ",dsrTemp)
                    print("Current temp: " , temp)
                    print("lightThreshold: ",lightThreshold)
                    print ("Current light level: ",light)
                    print("thresholdRelevant: ", thresholdRelevant)
                    print("==================================")
                elif light < lightThreshold and not thresholdRelevant:
                    #it will be expected that when system starts up at scheduled time 
                    #there will be no light. If statement accounts for this
                    if tm.time() - warmUpStartTime > allowedWarmUpTime:
                        thresholdRelevant = True
                        darkTime = tm.time()
                        print("adjust thresholdRelevant t0 true: ", thresholdRelevant)
                    print("======light < lightThreshold and not thresholdRelevant======")
                    print("Desired Temp: ",dsrTemp)
                    print("Current temp: " , temp)
                    print("lightThreshold: ",lightThreshold)
                    print ("Current light level: ",light)
                    print("thresholdRelevant: " ,thresholdRelevant)
                    print("==================================")
                elif light < lightThreshold and thresholdRelevant:
                    print("======light < lightThreshold and thresholdRelevant================")
                    print("Desired Temp: ",dsrTemp)
                    print("Current temp: " , temp)
                    print("lightThreshold: ",lightThreshold)
                    print ("Current light level: ",light)
                    print("thresholdRelevant: ", thresholdRelevant)
                    timeDark = tm.time() - darkTime
                    print("Time in dark: ",timeDark)
                    print("==================================")
                    if timeDark > darkLimit:
                        print("=====timeDark > darkLimit, Shutdown========")
                        thresholdRelevant = False
                        waiting = True
                        #send message to have heater node quit sampling
                        ser.write(b'T')
                        #turn off power
                        ser.write(b'F')
                        print("thresholdRelevant to False")
                        print("waiting to True")
                        print("Quit sampling and turn of power switch")
                        print("==================================")
                #=================================================================
        #isTemp check will allow system to determine if node lost power
        if not waiting and isTemp:
            if  ser.inWaiting():
                print("Lost Connection")
            if temp >= (dsrTemp + 2):
                ser.write(b'F')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("Power OFF! Temp: ", temp)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            elif temp <= (dsrTemp - 2):
                ser.write(b'O')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("Power ON! Temp: ", temp)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                #===========================================================================
except:
    print( "unexpected error:", sys.exc_info());



