import csv
import datetime
import math
import time
import collections
from collections import OrderedDict
import os.path

gravX = 0
gravY = 0
gravZ = 0

EDAHertz = 4
BVPHertz = 64
TEMPHertz = 4
ACCHertz = 32

#myDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))+"/" #Setting current dir
#myDir = os.path.split(os.path.abspath(myDir))[0]

myDir = dir_path = os.path.dirname(os.path.realpath(__file__))+"/"
participantID = os.path.split(os.path.abspath(myDir))[1] #Parent of parent directory as ParticipantID for the case of aquarium di Genova data

outputFile = "mergedBioData.csv" #Setting name of output file

print "Current Directory: ",myDir
print "Syncing data for Participant: ",participantID

def convertMilisToTime(milis):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(round(milis))))

def processAcceleration(x,y,z):
    #converting to G values: https://support.empatica.com/hc/en-us/articles/201608896-Data-export-and-formatting-from-Empatica-Connect-
    x = float(x) * 2/128
    y = float(y) * 2/128
    z = float(z) * 2/128
    #calculating effect of gravity
    alpha = 0.8
    global gravX
    global gravY
    global gravZ
    #Global variables for applying low pass filter on acceleration values
    gravX = alpha * gravX + (1 - alpha) * x;
    gravY = alpha * gravY + (1 - alpha) * y;
    gravZ = alpha * gravZ + (1 - alpha) * z;
    #removing gravity's effect: https://developer.android.com/reference/android/hardware/SensorEvent.html#values
    x = x - gravX
    y = y - gravY
    z = z - gravZ
    #total acceleration from all 3 axes: http://physics.stackexchange.com/questions/41653/how-do-i-get-the-total-acceleration-from-3-axes
    overall = math.sqrt(x*x+y*y+z*z)
    return {'x':x,'y':y,'z':z,'overall':overall}
    
def readFile(file):
    dict = OrderedDict() 
    print "-->Reading file:" + file
    with open(file, 'rb') as csvfile:
         reader = csv.reader(csvfile, delimiter='\n') 
         i=0;
         for row in reader:
             if(i == 0):
                 timestamp=row[0]
                 timestamp = float(timestamp)+3600*2#converts from string to float rounds and then to int
             elif(i == 1):
                 hertz=float(row[0])
             elif(i == 2):
                 dict[timestamp]=row[0]
                 #print ', '.join(row)
             else:
                 timestamp = timestamp + 1.0/hertz
                 #print timestamp
                 #print convertMilisToTime(timestamp)
                 dict[timestamp]=row[0]
             #print "HR Timestamp:",timestamp," exact Time: ",convertMilisToTime(timestamp)
             i = i + 1.0
    return dict

def readAccFile(file):
    dict = OrderedDict()
    print "-->Reading file:" + file
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        i=0;
        for row in reader:
            if(i == 0):
                timestamp = float(row[0])+3600*2#converts from string to float rounds and then to int
            elif(i == 1):    
                hertz=float(row[0])
            elif(i == 2):
                dict[timestamp]= processAcceleration(row[0],row[1],row[2])
            else:
                timestamp = timestamp + 1.0/hertz 
                dict[timestamp] = processAcceleration(row[0],row[1],row[2])
            i = i + 1
       
    return dict
#Reading IBI File
def readIBI_File(file):
    dict = OrderedDict()
    print "-->Reading file:" + file
    with open(file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        initialTimestamp = 0.0
        i = 0;
        for row in reader:
            if(i == 0):
                initialTimestamp = float(row[0])+3600*2
                print "Initial Timestamp ",initialTimestamp," exact Time: ",convertMilisToTime(initialTimestamp)
            else:
                timestamp = initialTimestamp + round(float(row[0]),1)
                dict[timestamp] = float(row[1])
                #print "IBI timestamp",timestamp," exact Time: ",convertMilisToTime(timestamp)
            i = i + 1
    return dict
    
ACC = {}
ACC = readAccFile(myDir+'ACC.csv')    

HR = {}
HR = readFile(myDir+'HR.csv')

EDA = {}
EDA = readFile(myDir+'EDA.csv')

BVP = {}
BVP = readFile(myDir+'BVP.csv')

TEMP = {}
TEMP = readFile(myDir+'TEMP.csv')

IBI = {}
IBI = readIBI_File(myDir+'IBI.csv')

#merging all files at a sampling rate of 1 Hz
count = 0 #count of how many timestamps are the same
total = 0 #total of measurements with the same timestamp

start_time = convertMilisToTime(time.time()+3600*2)

with open(outputFile,'w') as f1:
    writer=csv.writer(f1, delimiter=',',lineterminator='\n',)
    row ="ID","Timestamp","Hour","HRV","EDA","BVP","TEMP","ACC_X","ACC_Y","ACC_Z","ACC_Overall","SumIBI","Beats"
    writer.writerow(row)    
    for timestampHR, hr in HR.items():
        timestamp = convertMilisToTime(timestampHR)
        hour = timestamp.split(" ")#splitting timestamp and keeping hour for importing to SPSS
        #merging with EDA
        i = 0.0
        total = 0.0
        count = 0
        meanEDA = 0.0
        while i < 1.0:
            if (timestampHR + i in EDA):
                total = total + float(EDA[timestampHR+i])
                count = count+1
            i = i + 1.0/EDAHertz
        if(count > 0):
            meanEDA = total/count
        print "Merging HRV and EDA at ", timestamp, " HRV: ",hr," EDA ",meanEDA, " count: ",count
        #merging with BVP 
        i = 0.0
        total = 0.0
        count = 0
        meanBVP = 0.0
        while i < 1.0:
            if (timestampHR + i in BVP):
                total = total + float(BVP[timestampHR+i])
                count = count+1
            i = i + 1.0/BVPHertz
        if(count > 0):
            meanBVP = total/count
        print "Merging HRV and BVP at ", timestamp, " HRV: ",hr," BVP ",meanBVP, " count: ",count
        #merging with TEMP
        i = 0.0
        total = 0.0
        count = 0
        meanTemp = 0.0
        while i < 1.0:
            if (timestampHR + i in TEMP):
                total = total + float(TEMP[timestampHR+i])
                count = count+1
            i = i + 1.0/TEMPHertz
        if(count > 0):
            meanTEMP = total/count
        print "Merging HRV and TEM at ", timestamp, " HRV: ",hr," TEM ",meanTEMP, " count: ",count  
        #merging with ACC
        i = 0.0
        totalX = 0.0
        totalY = 0.0
        totalZ = 0.0
        totalOverall = 0.0
        count = 0
        meanX = 0.0
        meanY = 0.0
        meanZ = 0.0
        meanOverall = 0.0
        while i < 1.0:
            if (timestampHR + i in ACC):
                totalX = totalX + float(ACC[timestampHR+i]['x'])
                totalY = totalY + float(ACC[timestampHR+i]['y'])
                totalZ = totalZ + float(ACC[timestampHR+i]['z'])
                totalOverall = totalOverall + float(ACC[timestampHR+i]['overall'])
                count = count+1
            i = i + 1.0/ACCHertz
        if(count > 0):
            meanX = totalX/count
            meanY = totalY/count
            meanZ = totalZ/count
            meanOverall = totalOverall/count
        print "Merging HRV and ACC at ", timestamp, " HRV: ",hr," ACC ",meanOverall, " count: ",count
        #merging with IBI in 1 second timeframes: Sums up all IBI occurring in 1 sec time frame.
        i = 0.0
        total = 0.0
        count = 0
        sumIBI = 0.0
        while i < 1.0:
            if(timestampHR + i in IBI):
                #print "Timestamps matched-- HR:",timestampHR," IBI: ",timestampHR+i
                total = total + float(IBI[timestampHR+i])
                count = count + 1
            i = i + 0.1
        if(count > 0):
            sumIBI = total
        print "Merging HRV and IBI at ", timestamp," milis: ",timestampHR," HRV: ",hr, " Sum IBI: ",sumIBI, " count: ",count
        
        row = participantID,timestamp,hour[1],hr,meanEDA,meanBVP,meanTEMP,meanX,meanY,meanZ,meanOverall,sumIBI,count
        writer.writerow(row)
print "--------------------------------------------------------------------------------"        
print "Synced data for Participant: ",participantID
print "Start time: ", start_time, " End time: ", convertMilisToTime(time.time()+3600*2)
print "Results stored in ",outputFile
   