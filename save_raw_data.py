import csv
import serial.tools.list_ports
import time
import datetime
import statistics

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

distance = 50
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portList = []

# display port options
for onePort in ports:
    portList.append(str(onePort))
    print(str(onePort))

# user input for COM port on PC
com_num = input("select Port: COM")

for x in range(0,len(portList)):
    # display port selection for user (lets user double check)
    if portList[x].startswith("COM" + str(com_num )):
        portVar = "COM" + str(com_num)
        print(portList[x])

serialInst.baudrate = 9600
serialInst.port = portVar
serialInst.open()


output = []

data_list = []
data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Channel", "Distance (m)", "Sensor GPS Coords", "Tag GPS Coords"])  #Added distance and GPS for now

summaries_list = []
summaries_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Scheduled Status (STS)", "Detection Count (DC)", "Ping Count (PC)", "Line Voltage (LV) [V]", "Internal Receiver Temperature", "Detection Memory Used", "Raw Memory Used", "Tilt Information [G]", "Output Noise", "Output PPM Noise"])

for line in output:
    line = line.split(',')
    line = [s[s.find("=")+1:].strip() for s in line]
    line.append(distance)   #Adds distance for now
    line.append(self.TAG_COORDINATES)   #Adds coords for now
    line.append(self.SENSOR_COORDINATES)
    
    for s in line:
        try:
            s = float(s)
        except:
            pass  

    if len(line) < 14:
        data_list.append(line)
    else:
        summaries_list.append(line)

with open("data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

with open("summaries.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)
