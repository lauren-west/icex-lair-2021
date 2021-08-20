import datetime
import csv
from geopy.distance import geodesic

# CSV for sensor 1
# SENSOR1: 33.480503, -117.733113
# TAG: 33.48086355960937, -117.7337781857398
# loop and change values
# initialize

# def get_distance_from_gps_locations(self):
#         """ Returns:
#           distance (double): dist in meters between tag and sensor gps coords
#         """
#         return geodesic(self.TAG_COORDINATES, self.SENSOR_COORDINATES).m

data_list = []
data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Channel", "Distance (m)", "Sensor GPS Coords", "Tag GPS Coords"])

receiver_serial_num = "457012"
transmitter_id = "65477"
distance = 0
# sensor 1
# sensor_lat = 33.480503
# sensor_long = -117.733113

tag_lat = 33.480447
tag_long = -117.734242

# sensor 2
sensor_lat = 33.481380
sensor_long = -117.734245

time_change = datetime.timedelta(0,8, 179000)
tof = datetime.timedelta(0,0,0)
original_dt =  datetime.datetime.strptime('2021-07-22 11:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
dt =  datetime.datetime.strptime('2021-07-22 11:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
end_dt = dt + datetime.timedelta(0, 0, 0, 0, 20) 
# delta = timedelta(
# ...     days=50,
# ...     seconds=27,
# ...     microseconds=10,
# ...     milliseconds=29000,
# ...     minutes=5,
# ...     hours=8,
# ...     weeks=2
# ... )
count = 0
while dt < end_dt:
    line = []
    line.append(receiver_serial_num) # receiver serial num (changes with each csv)
    line.append("000")
    line.append(dt) # needs to (change according to shark movement)
    line.append("A69-1602")
    line.append(transmitter_id) # tag id
    line.extend(["82.0", "38.5", "#97"]) # dont change
    line.append(str(distance))  # actual distance (accurate and contrived for PF?)
    line.append("("+ str(sensor_lat)+ "," + str(sensor_long) + ")") # "Sensor GPS Coords" (given once?, must be accurate, not right next to each other)
    line.append("("+ str(tag_lat)+ "," + str(tag_long) + ")") # "tag GPS Coords" (given once?, must be accurate)
    data_list.append(line)

    # MAKE SHARK MOVE:

    # edit gps tag coord lat by small value
    tag_lat += 0.00008
    # get distance 
    distance = geodesic((tag_lat, tag_long), (sensor_lat, sensor_long)).m
    # create new dt (8.179 + tof ) # tof calculated from ^ distance
    tof = distance / 1500
    dt = original_dt + time_change * count + datetime.timedelta(seconds=tof) 
    count += 1

# rename other to be "sensor2_fake_collab.csv"
with open("sensor2_fake_collab.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

#############################################################################
# t01  = datetime.datetime.strptime('2021-07-22 11:14:51.858', '%Y-%m-%d %H:%M:%S.%f')
# l1 =  [t01]
# tof = datetime.timedelta(0,0, 0)
# time_change = datetime.timedelta(0,8, 179000)

# for i in range(1,120):
#     if i == 40:
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




