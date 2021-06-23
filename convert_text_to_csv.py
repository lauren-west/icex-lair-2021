import csv
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
    try:
        if serialInst.in_waiting:
            packet = serialInst.readline()
            output.append(packet)
            #print(packet.decode('utf').rstrip('\n'))
    except:
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

        print(data_list)
        print(summaries_list)

        with open("data.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(data_list)

        with open("summaries.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(summaries_list)