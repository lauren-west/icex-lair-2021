import csv

with open('CO_Preliminary_Test_Data.txt') as f:
    lines = f.readlines()

# data_list is 2D array of strings of data
# rows are lines, and cols are the specific measurements
data_list = []

for line in lines:
    line = line.split(',')
    line = [s[s.find("=")+1:].strip() for s in line]
    data_list.append(line)

print(data_list)


with open("output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

