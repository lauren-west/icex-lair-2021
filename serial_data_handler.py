import csv
import serial.tools.list_ports
import time
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

from geopy.distance import geodesic


class Serial_Data_Handler():

    TIME_TO_RUN = 120 # seconds

    # consider making these global
    # SENSOR_GPS_COORDS = (lat, longit)
    # TAG_GPS_COORDS = (lat, longit)


    def __init__(self) -> None:
        pass

    def get_settings(self):
        TIME_TO_RUN = input("Time to run in seconds")
        SENSOR_GPS_COORDS = (input("Enter sensor latitude"), input("Enter sensor longitude"))
        TAG_GPS_COORDS = (input("Enter tag latitude"), input("Enter tag longitude"))

        return TIME_TO_RUN, SENSOR_GPS_COORDS, TAG_GPS_COORDS

    def get_serial_data(self, ports, serialInst):

        portList = []

        # display port options
        for onePort in ports:
            portList.append(str(onePort))
            print(str(onePort))

        # user input for COM port on PC
        com_num = input("select Port: COM")
        
        for x in range(0,len(portList)):
            # display port selection for user (lets user double check)
            if portList[x].startswith("COM" + str(com_num )):
                portVar = "COM" + str(com_num)
                print(portList[x])

        serialInst.baudrate = 9600
        serialInst.port = portVar
        serialInst.open()

    def get_gps_location(self):
        """ Returns:
          sensor gps coordinates (tuple): (lattitude, longitude)
          tag gps coordinates (tuple): (lattitude, longitude)
          distance (double): dist in meters
        """
        sensor_latitude = 33.75230
        sensor_longitude = -118.12829
        sensor_coords = (sensor_latitude, sensor_longitude)

        tag_latitude = 33.75227  
        tag_longitude = -118.12857
        tag_coords = (tag_latitude, tag_longitude)

        distance = 50

        if input("Are you using distance or GPS coordinates? (Type distance or GPS): ").lower() == distance:
            distance = input("What is the distance? (Can enter placeholders 1, 2, ..., 10, 11 for now): ")
        else:
            latitude = input("Input GPS latitude: ")
            longitude = input("Input GPS longitude: ")
            distance = geodesic(tag_coords, sensor_coords).km

        return sensor_coords, tag_coords, distance

    def make_data_and_summaries_lists(self, output, distance, sensor_gps_coords, tag_gps_coords):
        data_list = []
        data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Channel", "Distance (m)", "Sensor GPS Coords", "Tag GPS Coords"])  #Added distance and GPS for now

        summaries_list = []
        summaries_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Scheduled Status (STS)", "Detection Count (DC)", "Ping Count (PC)", "Line Voltage (LV) [V]", "Internal Receiver Temperature", "Detection Memory Used", "Raw Memory Used", "Tilt Information [G]", "Output Noise", "Output PPM Noise"])

        for line in output:
            line = line.split(',')
            line = [s[s.find("=")+1:].strip() for s in line]
            line.append(distance)   #Adds distance for now
            line.append(sensor_gps_coords)   #Adds coords for now
            line.append(tag_gps_coords)
            
            for s in line:
                try:
                    s = float(s)
                except:
                    pass  

            if len(line) < 14:
                data_list.append(line)
            else:
                summaries_list.append(line)
        
        return data_list, summaries_list

    def make_delta_t(self, data_list):
        delta_t = ["Times of Transmission"] # [8, 8, 8, 8,8 ,8, 8, ... , 8.001, 8.002]

        for i in range(2, len(data_list)):
            print(data_list[i-1][2])
            print(data_list[i][2])
            past_datetime = datetime.datetime.strptime(data_list[i-1][2], '%Y-%m-%d %H:%M:%S.%f')
            current_datatime = datetime.datetime.strptime(data_list[i][2], '%Y-%m-%d %H:%M:%S.%f')
            if (current_datatime - past_datetime).total_seconds() > 10:
                pass
            else:
                total_seconds = (current_datatime - past_datetime).total_seconds()
                delta_t.append(total_seconds)
        return delta_t

    def create_histogram(self, iteration, delta_t):
        """ 
            Creates and saves histogram in file
        """
        delta_t_np = np.array(delta_t[1:])

        NUM_OF_BINS = 20 # Anywhere from 5-20 with 20 being with at least 1000 data points
        plt.hist(delta_t_np, NUM_OF_BINS)
        plt.title("Time of Transmission Histogram")
        plt.xlabel("time (s)")
        plt.ylabel("Frequency")
        plt.savefig(iteration + "_histogram.png")
        plt.show()

    def get_predicted_times(self, delta_t):
        predicted_times_of_transmission = ["Predicted Times of Transmission"]
        t0 = 0
        delta_t_avg  = sum(delta_t[1:]) / (len(delta_t) - 1)

        for i in range(1, len(delta_t)):
            predicted_times_of_transmission.append(t0 + i * delta_t_avg)

        return predicted_times_of_transmission

    def get_real_time(self, delta_t):
        prior_sum = delta_t[1]
        real_times_of_transmission = ["Real Time of Transmission"]

        for i in range(1, len(delta_t)):
            real_times_of_transmission.append(prior_sum)
            prior_sum += delta_t[i]

        return real_times_of_transmission

    def get_error_tot(self, predicted_times_of_transmission, real_times_of_transmission):
        error_tot = ["Error"]
        
        for i in range(1, len(predicted_times_of_transmission)):
            error_tot.append(predicted_times_of_transmission[i] - real_times_of_transmission[i])

        return error_tot

    def create_csvs(self, iteration, data_list, summaries_list, times_list):
        ###### Creating data, summary, and error csvs #####
        with open(iteration + ".csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(data_list)

        with open(iteration + "_summaries.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(summaries_list)

        with open(iteration + "_calculated_error_values.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(times_list)

    def create_plots(self, iteration):
        # Read in the data
        # 
        # for read_csv, use header=0 when row 0 is a header row 

        filename = iteration + '.csv'     # TODO: Change name to reflect other half
        df = pd.read_csv(filename, header=0)   # read the file w/header row #0
        print(f"{filename} : file read into a pandas dataframe.")

        #df_clean = df.dropna()
        df_clean = df

        # Plot using Seaborn
        sns.lmplot(x='Distance (m)', y='Signal Level (dB)', fit_reg=True, data=df_clean, hue='Transmitter ID Number')
        
        # Tweak these limits
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.savefig(iteration + "_signal_plot.png")    # TODO: Change name

        # Plot using Seaborn
        sns.lmplot(x='Distance (m)', y='Noise-Level (dB)', fit_reg = True, data=df_clean, hue='Transmitter ID Number')
        
        # Tweak these limits
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.savefig(iteration + '_noise_plot.png')  # TODO: Change name

        # ADD TO PLOT OTHER STUFF
        # filename = iteration + '_calculated_error_values.csv'     # TODO: Change name to reflect other half
        # df = pd.read_csv(filename, header=0)   # read the file w/header row #0
        # print(f"{filename} : file read into a pandas dataframe.")


if __name__ == '__main__':
    handler = Serial_Data_Handler()

    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()

    # consider this to make program more user-friendly. Otherwise, we will code in settings manually
    # TIME_TO_RUN, sensor_gps_coords, tag_gps_coords, distance = handler.get_settings()

    serial_port = handler.get_serial_data(ports, serialInst)
    sensor_gps_coords, tag_gps_coords, distance = handler.get_gps_location()

    iteration = "data_" + str(input("Iteration of data collection (Enter a number to not overwrite files): "))

    #Starts the stopwatch/counter
    t1_start = time.perf_counter()

    output = []

    while time.perf_counter() - t1_start < handler.TIME_TO_RUN:
        if serialInst.in_waiting:
            packet = serialInst.readline()
            print(packet.decode('utf').rstrip('\n'))
            output.append(packet.decode('utf').rstrip('\n'))
        
    # data_list is 2D array of strings of data
    # rows are lines, and cols are the specific measurements
    data_list, summaries_list = handler.make_data_and_summaries_lists(output, distance, sensor_gps_coords, tag_gps_coords)

    delta_t = handler.make_delta_t(data_list)
    handler.create_histogram(iteration, delta_t)

    # lists to get projected &  real tot & error between them
    predicted_times_of_transmission  = handler.get_predicted_times(delta_t)
    real_times_of_transmission  = handler.get_real_times(delta_t)
    error_tot = handler.get_error_tot(predicted_times_of_transmission, real_times_of_transmission)
    times_list = zip([delta_t, real_times_of_transmission, predicted_times_of_transmission, error_tot])

    # create csvs and plot
    handler.create_csvs(iteration, data_list, summaries_list, times_list)
    handler.creat_plots(iteration)
