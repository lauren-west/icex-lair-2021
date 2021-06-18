import csv

with open('06_18_2021_Tag_77_pHake_Lake_Data.txt') as f:
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

with open("bfs_data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

with open("bfs_summaries.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(summaries_list)

