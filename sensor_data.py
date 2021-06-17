import csv

with open('CO_Preliminary_Test_Data.txt') as f:
    lines = f.readlines()

# data_list is 2D array of strings of data
# rows are lines, and cols are the specific measurements
data_list = []

for line in lines:
    line = line.split(',')
    # for s in line:
    #     if s.find("=") != -1:
    #         s = s[s.find("=")+1:].strip()
    #         try:
    #             s= float(s)
    #         except:
    #             print(s, " not a float.")
            
    line = [s[s.find("=")+1:].strip() for s in line]

    for s in line:
        try:
            s = float(s)    # print statement showed this didn't its job?
        except:
            print(s, "not a float")
    
    data_list.append(line)

print(data_list)


with open("output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(data_list)

