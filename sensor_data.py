with open('CO_Preliminary_Test_Data.txt') as f:
    lines = f.readlines()

my_list = []

# data_list is 2D array of strings of data
# rows are lines, and cols are the specific measurements
data_list = []
count = 0

for line in lines:
    data_list.append(line.split(','))

print(data_list)