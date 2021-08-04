
import datetime
t01  = datetime.datetime.strptime('2021-07-22 11:14:51.858', '%Y-%m-%d %H:%M:%S.%f')
l1 =  [t01]
tof = datetime.timedelta(0,0, 0)
time_change = datetime.timedelta(0,8, 179000)

for i in range(1,120):
    if i ==40:
        tof = datetime.timedelta(0,0, 68490)
        print("TOF:", 100)
    elif i == 20:
        tof = datetime.timedelta(0,0, 34200)
        print("TOF:", 50)
    else:
        pass
    print(l1[i-1] + time_change + tof)
    print()
    l1.append(l1[i-1] + time_change + tof)


################################################################################

print()
print()
print()
################################################################################
t02  = datetime.datetime.strptime('2021-07-22 11:13:58.800', '%Y-%m-%d %H:%M:%S.%f')
l2 =  [t02]
tof = datetime.timedelta(0,0, 0)

for i in range(1,120):
    if i ==40:
        tof = datetime.timedelta(0,0, 68490)
        print("TOF:", 100)
    elif i == 20:
        tof = datetime.timedelta(0,0, 34200)
        print("TOF:", 50)
    else:
        pass
    print(l2[i-1] + time_change + tof)
    print()
    l2.append(l2[i-1] + time_change + tof)





