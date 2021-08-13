import datetime
import csv


# CSV for sensor 1
# SENSOR1: 33.480503, -117.733113
# TAG: 33.48086355960937, -117.7337781857398
# loop and change values
# initialize
data_list = []
data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Channel", "Distance (m)", "Sensor GPS Coords", "Tag GPS Coords"])

receiver_serial_num = "457012"
transmitter_id = "65477"
distance = 0
sensor_lat = 33.480503
sensor_long = -117.733113
tag_lat = 33.48086355960937
tag_long = -117.7337781857398

dt =  datetime.datetime.strptime('2021-07-22 11:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
end_dt = dt + datetime.timedelta(0, 0, 0, 0, 30)
while dt < end_dt:
    print(dt)
    line = []
    line.append(receiver_serial_num) # receiver serial num (changes with each csv)
    line.append("000")
    line.append(dt) # needs to (change according to shark movement)
    line.append("A69-1602")
    line.append(transmitter_id) # tag id
    line.extend(["82.0", "38.5", "0", "#97"]) # dont change
    line.append(str(distance))  # actual distance (accurate and contrived for PF?)
    line.append("("+ str(sensor_lat)+ "," + str(sensor_long) + ")") # "Sensor GPS Coords" (given once?, must be accurate, not right next to each other)
    line.append("("+ str(tag_lat)+ "," + str(tag_long) + ")") # "tag GPS Coords" (given once?, must be accurate)
    data_list.append(line)
    tof = datetime.timedelta(0,0, 100000) # change this to make this more accurate
    dt = dt + datetime.timedelta(0,8, 179000) + tof # (days, seconds, microseconds, milliseconds, minutes, hours, weeks)
    print(dt)
# with open("sensor1.csv", "w") as f:
#     writer = csv.writer(f)
#     writer.writerows(data_list)

##################################################################
# CSV for sensor 2
# SENSOR2: 33.480447,-117.734242
# TAG: 33.48086355960937, -117.7337781857398
receiver_serial_num = "457049"
transmitter_id = "65477"
distance = 0
sensor_lat = 33.480447
sensor_long = -117.734242
tag_lat =  33.48086355960937
tag_long = -117.7337781857398

# loop and change values
# line = []
# line.append(receiver_serial_num) # receiver serial num (changes with each csv)
# line.append("000")
# line.append(datetime.date) # needs to (change according to shark movement)
# line.append("A69-1602")
# line.append(transmitter_id) # tag id
# line.extend(["82.0", "38.5", "0", "#97"]) # dont change
# line.append(str(distance))  # actual distance (accurate and contrived for PF?)
# line.append("("+ str(sensor_lat)+ "," + str(sensor_long) + ")") # "Sensor GPS Coords" (given once?, must be accurate)
# line.append("("+ str(tag_lat)+ "," + str(tag_long) + ")") # "tag GPS Coords" (given once?, must be accurate)
# data_list.append(line)

# with open("sensor2.csv", "w") as f:
#     writer = csv.writer(f)
#     writer.writerows(data_list)

#############################################################################
# t01  = datetime.datetime.strptime('2021-07-22 11:14:51.858', '%Y-%m-%d %H:%M:%S.%f')
# l1 =  [t01]
# tof = datetime.timedelta(0,0, 0)
# time_change = datetime.timedelta(0,8, 179000)

# for i in range(1,120):
#     if i ==40:
#         tof = datetime.timedelta(0,0, 68490)
#         print("TOF:", 100)
#     elif i == 20:
#         tof = datetime.timedelta(0,0, 34200)
#         print("TOF:", 50)
#     else:
#         pass
#     print(l1[i-1] + time_change + tof)
#     print()
#     l1.append(l1[i-1] + time_change + tof)
###############################################################################

###############################################################################
# t02  = datetime.datetime.strptime('2021-07-22 11:13:58.800', '%Y-%m-%d %H:%M:%S.%f')
# l2 =  [t02]
# tof = datetime.timedelta(0,0, 0)

# for i in range(1,120):
#     if i ==40:
#         tof = datetime.timedelta(0,0, 68490)
#         print("TOF:", 100)
#     elif i == 20:
#         tof = datetime.timedelta(0,0, 34200)
#         print("TOF:", 50)
#     else:
#         pass
#     print(l2[i-1] + time_change + tof)
#     print()
#     l2.append(l2[i-1] + time_change + tof)




