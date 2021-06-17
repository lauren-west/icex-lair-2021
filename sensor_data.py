import csv

with open('CO_Preliminary_Test_Data.txt') as f:
    lines = f.readlines()

# data_list is 2D array of strings of data
# rows are lines, and cols are the specific measurements
data_list = []

for line in lines:
    data_list.append(line.split(','))

with open("output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

