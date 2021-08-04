
import datetime
t0  = datetime.datetime.strptime('2021-07-22 11:14:51.858', '%Y-%m-%d %H:%M:%S.%f')
# t0 = datetime.datetime.strptime('2021-07-22 11:13:58.800', '%Y-%m-%d %H:%M:%S.%f')
time_change = datetime.timedelta(0,8, 179000)
tof50 = datetime.timedelta(0,0, 34200)
tof100 = datetime.timedelta(0,0, 68490)

for k in range(37, 120):
# for k in range(44, 120):
    print(t0 + (time_change * k) + tof100) 


