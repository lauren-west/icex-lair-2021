# libraries
import numpy as np
import pandas as pd
import datetime


import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

import csv
import serial.tools.list_ports
import time

################ Taking in Inputs and Converting into CSV ################
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portList = []

for onePort in ports:
   portList.append(str(onePort))
   print(str(onePort))

val = input("select Port: COM")

print(val)

for x in range(0,len(portList)):
  if portList[x].startswith("COM" + str(val)):
      portVar = "COM" + str(val)
      print(portList[x])

serialInst.baudrate = 9600
serialInst.port = portVar
serialInst.open()

#Starts the stopwatch/counter
t1_start = time.perf_counter()

output = []

# 15 minutes = (10**11)*9) nanoseconds
while time.perf_counter() - t1_start < 140:
    if serialInst.in_waiting:
        packet = serialInst.readline()
        print(packet.decode('utf').rstrip('\n'))
        output.append(packet.decode('utf').rstrip('\n'))
    
print(output)
# data_list is 2D array of strings of data
# rows are lines, and cols are the specific measurements

data_list = []
data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Channel"])

summaries_list = []
summaries_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Scheduled Status (STS)", "Detection Count (DC)", "Ping Count (PC)", "Line Voltage (LV) [V]", "Internal Receiver Temperature", "Detection Memory Used", "Raw Memory Used", "Tilt Information [G]", "Output Noise", "Output PPM Noise"])

for line in output:
    line = line.split(',')
    line = [s[s.find("=")+1:].strip() for s in line]

    for s in line:
        try:
            s = float(s)
        except:
            pass  

    if len(line) < 14:
        data_list.append(line)
    else:
        summaries_list.append(line)


## histogram stuff ##
delta_t_list = []
for i in range(1, len(data_list)):
    past_datetime = datetime.datetime.strptime(data_list[i-1][2], '%Y-%m-%d %H:%M:%S.%f')
    current_datatime = datetime.datetime.strptime(data_list[i][2], '%Y-%m-%d %H:%M:%S.%f')
    total_seconds = (current_datatime - past_datetime).total_seconds()
    delta_t_list.append(total_seconds)

plt.hist(delta_t_list, 10)  # 10 is our number of "bins"
plt.show()
######################

print(data_list)
print(summaries_list)

with open("data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

with open("summaries.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(summaries_list)

################ Taking in CSV and Plotting ################
# Read in the data
# 
# for read_csv, use header=0 when row 0 is a header row 

filename = 'data.csv'     # TODO: Change name to reflect other half
df = pd.read_csv(filename, header=0)   # read the file w/header row #0
print(f"{filename} : file read into a pandas dataframe.")

df_clean = df.dropna()

# Plot using Seaborn
sns.lmplot(x='Distance (m)', y='Signal Level (dB)', fit_reg=True, data=df_clean, hue='Transmitter ID Number')
 
# Tweak these limits
plt.ylim(30, None)
plt.xlim(0, 58)
plt.savefig("signal_plot.png")    # TODO: Change name

# Plot using Seaborn
sns.lmplot(x='Distance (m)', y='Noise-Level (dB)', fit_reg = True, data=df_clean, hue='Transmitter ID Number')
 
# Tweak these limits
plt.ylim(18, None)
plt.xlim(0, 58)
plt.savefig('noise_plot.png')  # TODO: Change name 
