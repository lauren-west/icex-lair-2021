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

#from geopy import distance

################ Taking in Inputs and Converting into CSV ################
ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portList = []

for onePort in ports:
   portList.append(str(onePort))
   print(str(onePort))

val = input("select Port: COM")

# Add GPS question for distance calculation
gps = input("Input gps coord: ")
distance = input("What is the distance? (Can enter 1, 2, ..., 10, 11 for now): ")
iteration = "data_" + str(input("Iteration of data collection (Enter a number to not overwrite files): "))

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

TIME_TO_RUN = 66
while time.perf_counter() - t1_start < TIME_TO_RUN:
    if serialInst.in_waiting:
        packet = serialInst.readline()
        print(packet.decode('utf').rstrip('\n'))
        output.append(packet.decode('utf').rstrip('\n'))
    
# print(output)

# data_list is 2D array of strings of data
# rows are lines, and cols are the specific measurements

data_list = []
data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Channel", "Distance (m)", "GPS Coords"])  #Added distance and GPS for now

summaries_list = []
summaries_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Scheduled Status (STS)", "Detection Count (DC)", "Ping Count (PC)", "Line Voltage (LV) [V]", "Internal Receiver Temperature", "Detection Memory Used", "Raw Memory Used", "Tilt Information [G]", "Output Noise", "Output PPM Noise"])

for line in output:
    line = line.split(',')
    line = [s[s.find("=")+1:].strip() for s in line]
    line.append(distance)   #Adds a fake distance for now
    line.append(gps)   #Adds a fake distance for now
    

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
delta_t = ["Times of Transmission"] # [8, 8, 8, 8,8 ,8, 8, ... , 8.001, 8.002]

for i in range(2, len(data_list)):
    print(data_list[i-1][2])
    print(data_list[i][2])
    past_datetime = datetime.datetime.strptime(data_list[i-1][2], '%Y-%m-%d %H:%M:%S.%f')
    current_datatime = datetime.datetime.strptime(data_list[i][2], '%Y-%m-%d %H:%M:%S.%f')
    total_seconds = (current_datatime - past_datetime).total_seconds()
    delta_t.append(total_seconds)

NUM_OF_BINS = 20 # Anywhere from 5-20 with 20 being with at least 1000 data points
plt.hist(delta_t[1:], NUM_OF_BINS)
plt.show()
plt.savefig(iteration + "_histogram.png")
######################

## error stuff ##
predicted_times_of_transmission = ["Predicted Times of Transmission"]
error_delta_ts = ["Error"]
t0 = 0
delta_t_avg  = sum(delta_t[1:]) / (len(delta_t) - 1)

for i in range(1, len(delta_t)):
    predicted_times_of_transmission.append(t0 + i * delta_t_avg)  # [8, 16, 24, ..., 64]

prior_sum = delta_t[1]
real_time_of_transmission = ["Real Time of Transmission"]

for i in range(1, len(predicted_times_of_transmission)):
    real_time_of_transmission.append(prior_sum)
    error_delta_ts.append(predicted_times_of_transmission[i] - prior_sum)
    prior_sum += delta_t[i]
    

    # error_delta_ts.append(predicted_times_of_transmission[1:i] - sum(delta_t[1:i]))

times_list = [delta_t, real_time_of_transmission, predicted_times_of_transmission, error_delta_ts]
######################

# print(data_list)
# print(summaries_list)

with open(iteration + ".csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

with open(iteration + "_summaries.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(summaries_list)

with open(iteration + "_calculated_error_values.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(times_list)

################ Taking in CSV and Plotting ################
# Read in the data
# 
# for read_csv, use header=0 when row 0 is a header row 

# filename = iteration + '.csv'     # TODO: Change name to reflect other half
# df = pd.read_csv(filename, header=0)   # read the file w/header row #0
# print(f"{filename} : file read into a pandas dataframe.")

# #df_clean = df.dropna()
# df_clean = df

# # Plot using Seaborn
# sns.lmplot(x='Distance (m)', y='Signal Level (dB)', fit_reg=True, data=df_clean, hue='Transmitter ID Number')
 
# # Tweak these limits
# plt.ylim(30, None)
# plt.xlim(0, 58)
# plt.savefig("signal_plot.png")    # TODO: Change name

# # Plot using Seaborn
# sns.lmplot(x='Distance (m)', y='Noise-Level (dB)', fit_reg = True, data=df_clean, hue='Transmitter ID Number')
 
# # Tweak these limits
# plt.ylim(18, None)
# plt.xlim(0, 58)
# plt.savefig('noise_plot.png')  # TODO: Change name

# ADD TO PLOT OTHER STUFF
# filename = iteration + '_calculated_values.csv'     # TODO: Change name to reflect other half
# df = pd.read_csv(filename, header=0)   # read the file w/header row #0
# print(f"{filename} : file read into a pandas dataframe.")
