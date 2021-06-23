#### Caitlyn's serial code ####
import serial.tools.list_ports
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

output = []
while True:
  if serialInst.in_waiting:
      packet = serialInst.readline()
      output.append(packet)
    #   print(packet.decode('utf').rstrip('\n'))
################################

print(output)

#####csv version#######
import serial
import time
import csv

# ser = serial.Serial('/dev/tty.usbserial-AB0L7DSC') # port on Lauren's Mac: /dev/tty.usbserial-AB0L7DSC
# ser = serial.Serial(port = "COM5", baudrate=9600, bytesize=8) # port on Caitlyn's Windows: COM5
ser = serial.Serial('/dev/tty.usbserial-AB0L7DSC') # change as needed
ser.flushInput()


while True:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = float(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        print(decoded_bytes)
        with open("test_data.csv","a") as f:
            writer = csv.writer(f,delimiter=",")
            writer.writerow([time.time(), decoded_bytes])  
    except:
        print("Keyboard Interrupt")
        break

# csv version#######

with open('test_data.csv') as f:
    lines = f.readlines()

# data_list is 2D array of strings of data
# rows are lines, and cols are the specific measurements
data_list = []
data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Channel"])

summaries_list = []
summaries_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Scheduled Status (STS)", "Detection Count (DC)", "Ping Count (PC)", "Line Voltage (LV) [V]", "Internal Receiver Temperature", "Detection Memory Used", "Raw Memory Used", "Tilt Information [G]", "Output Noise", "Output PPM Noise"])

for line in lines:
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

print(data_list)
print(summaries_list)

with open("data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

with open("summaries.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(summaries_list)

