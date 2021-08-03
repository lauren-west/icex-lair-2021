
import datetime
t0  = datetime.datetime.strptime('2021-07-22 11:14:51.858', '%Y-%m-%d %H:%M:%S.%f')
# t0 = datetime.datetime.strptime('2021-07-22 11:13:58.800', '%Y-%m-%d %H:%M:%S.%f')
time_change = datetime.timedelta(0,8, 179000)
tof = datetime.timedelta(0,0, 34200)

for k in range(37, 100):
# for k in range(44, 89):
    print(t0 + (time_change * k) + tof) 


