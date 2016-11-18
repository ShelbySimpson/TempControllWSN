import datetime

#get the time the heater will turn on to start heating. Based on user input
def getStartUpTime(time):
    time0 = time.split(":")
    time1 = [int(i) for i in time0]
    time2 = datetime.time(time1[0],time1[1])
    return time2
    #probably not part of the MVP, but eventually using
    #standard time format will avial - 
    #pmAm = time[-2:]
    #format = '%H:%M%p'
    #time = time[:-2]
    #print("this is the time: ",time2)
    #my_date = datetime.datetime.strptime(time, format)
    #print(my_date.strftime(format))
    #print(my_date)
