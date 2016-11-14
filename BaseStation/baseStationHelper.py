import datetime

#get the time the heater will turn on to start heating. Based on user input
def getStartUpTime(time):
    time0 = time.split(":")
    time1 = [int(i) for i in time0]
    time2 = datetime.time(time1[0],time1[1])
    print("this is the time: ",time2)