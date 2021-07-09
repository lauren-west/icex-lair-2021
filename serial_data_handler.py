import csv
import serial.tools.list_ports
import time
import datetime
import statistics
import os
import os.path
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="darkgrid")

from geopy.distance import geodesic


class Serial_Data_Handler():

    TIME_TO_RUN = 120 # seconds
    NUM_OF_BINS = 10 # Anywhere from 5-20 with 20 being with at least 1000 data points
    SPEED_OF_SOUND = 1500  # m/s

    TAG_COORDINATES = (34.109135,-117.71281)
    SENSOR_COORDINATES = (34.109172,-117.71241)

    def __init__(self) -> None:
        pass

    def get_serial_data(self, ports, serialInst):
        """ 
        get_serial_data opens com port on PC in vs code
        returns: None
        """

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

    def get_distance_from_gps_locations(self):
        """ Returns:
          distance (double): dist in meters between tag and sensor gps coords
        """
        return geodesic(self.TAG_COORDINATES, self.SENSOR_COORDINATES).m

    def make_data_and_summaries_lists(self, output, distance):
        """ Returns:
          data_list (list of lists): rows are serial data lines, columns are 
            features (example: Receiver Serial Number)
          summaries_list (list of lists): contains rows that are data "summaries," 
            features include "Ping Count (PC)", "Line Voltage (LV) [V]"
        """
        data_list = []
        data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", "Distance (m)", "Channel", "Tag GPS Coords", "Sensor GPS Coords", "Time (s)", "Time of Flight (s)", "Predicted Distance (m)"])  #Added distance and GPS for now

        summaries_list = []
        summaries_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", "Scheduled Status (STS)", "Detection Count (DC)", "Ping Count (PC)", "Line Voltage (LV) [V]", "Internal Receiver Temperature", "Detection Memory Used", "Raw Memory Used", "Tilt Information [G]", "Output Noise", "Output PPM Noise", "Distance (m)", "Tag GPS Coords", "Sensor GPS Coords", "Time (s)", "Time of Flight (s)", "Predicted Distance (m)"])
        
        initial_time = None        # Used to calculate time elapsed
        counter = 0

        first_timestamp = None
        
        try:
            with open('data_1.csv', "r") as f:
                reader = csv.reader(f)
                _ = next(reader)
                row1 = next(reader)
                first_timestamp = datetime.datetime.strptime(row1[2], '%Y-%m-%d %H:%M:%S.%f')
        except:
            line = output[0].split(',')
            line = [s[s.find("=")+1:].strip() for s in line]
            first_timestamp = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S.%f')

        for line in output:
            line = line.split(',')
            line = [s[s.find("=")+1:].strip() for s in line]
            
            if counter == 0:
                initial_time = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S.%f')
                counter += 1

            line.append(distance)   #Adds distance for now
            line.append(self.TAG_COORDINATES)   #Adds tag coords for now
            line.append(self.SENSOR_COORDINATES)   #Adds sensor coords for now

            current_datatime = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S.%f')

            line.append((current_datatime - initial_time).total_seconds())

            time_of_flight = (current_datatime - first_timestamp).total_seconds() % 8.179
            line.append(time_of_flight)
            line.append(time_of_flight * self.SPEED_OF_SOUND)

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
        """ Returns:
          delta_t (list): delta_t contains doubles, each one indicating the time difference
          from a present ping to the adjacent past ping in data_list. This is called
          the Time of Transmission
        """
        delta_t = ["Times of Transmission"] # [8, 8, 8, 8,8 ,8, 8, ... , 8.001, 8.002]

        for i in range(2, len(data_list)):
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

        NUM_OF_BINS = 10 # Anywhere from 5-20 with 20 being with at least 1000 data points
        plt.hist(delta_t_np, NUM_OF_BINS)
        plt.title("Time of Transmission Histogram")
        plt.xlabel("time (s)")
        plt.ylabel("Frequency")
        plt.savefig(iteration + "_histogram.png")
        plt.show()

    def get_predicted_times(self, delta_t):
        """ Returns:
          predicted_times_of_transmission (list): contains doubles, each predicted 
          time calculated by using an average tot (average delta_t) before drift.
          t_predicted = t0 + (k * delta_t_avg)

          Note: there may be a better way to get delta_t_avg than the method below
        """
        predicted_times_of_transmission = ["Predicted Times of Transmission"]
        t0 = 0
        # dilemma: What should delta t avg be?
        # delta_t_avg  = sum(delta_t[1:]) / (len(delta_t) - 1)
        delta_t_avg = 8.179
        # delta_t_avg  = sum(delta_t[1:10]) / (len(delta_t[1:10]))
        print("avg: ", delta_t_avg)
        
        for i in range(1, len(delta_t)):
            predicted_times_of_transmission.append(t0 + i * delta_t_avg)

        return predicted_times_of_transmission

    def get_real_times(self, delta_t):
        """ Returns:
            real_times_of_transmission (list): real times (seconds) as doubles
            continuous record of ping times in seconds, starting with the first ping
            example: (8, 16, 24, 32)
        """
        real_times_of_transmission = ["Real Time of Transmission"]
        prior_sum = 0
        for i in range(1, len(delta_t)):
            prior_sum += delta_t[i]
            real_times_of_transmission.append(prior_sum)

        return real_times_of_transmission

    def get_error_tot(self, predicted_times_of_transmission, real_times_of_transmission):

        error_tot = ["Error"]
        
        for i in range(1, len(predicted_times_of_transmission)):
            error_tot.append(real_times_of_transmission[i] - predicted_times_of_transmission[i])

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

        filename = iteration + '.csv'
        df = pd.read_csv(filename, header=0, index_col=False)   # read the file w/header row #0
        print(f"{filename} : file read into a pandas dataframe.")

        #df_clean = df.dropna()
        #df_clean = df

        # Plot using Seaborn
        sns.lmplot(x='Time (s)', y='Signal Level (dB)', fit_reg=True, data=df, hue='Transmitter ID Number')
        
        # Tweak these limits
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.savefig(iteration + "_signal_plot.png")

        # Plot using Seaborn
        sns.lmplot(x='Time (s)', y='Noise-Level (dB)', fit_reg = True, data=df, hue='Transmitter ID Number')
        
        # Tweak these limits
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.savefig(iteration + '_noise_plot.png')


        plt.hist(df['Time of Flight (s)'], self.NUM_OF_BINS)
        plt.title("Time of Flight")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency")
        plt.savefig("time_of_flight_" + iteration + ".png")

        
        plt.hist(df['Predicted Distance (m)'], self.NUM_OF_BINS)
        plt.title("Distance Predictions")
        plt.xlabel("Distance (m)")
        plt.ylabel("Frequency")
        plt.savefig("time_of_flight_distance_predictions_" + iteration + ".png")
        plt.show()
        

    def create_final_plots(self):
        AllFiles = list(os.walk("."))  #Walks everything inside current directory

        df_list = []
        delta_t_values = np.array([])
        error_values = np.array([])

        _, _, LoFiles = AllFiles[0] 

        for filename in LoFiles:
            if filename[-3:] == "csv" and (len(filename) == 10 or len(filename) == 11):    
                path = os.getcwd() + "/" + filename 
                df = pd.read_csv(path, engine='python', header=0, index_col=False)
                df_list.append(df)

            elif filename[-3:] == "csv" and "calculated_error" in filename:  
                path = os.getcwd() + "/" + filename 
                df = pd.read_csv(path, engine='python', header=None, index_col=False)
                delta_t_values = np.concatenate((delta_t_values, df.values[0][1:]))
                error_values = np.concatenate((error_values, df.values[3][1:]))

        # for item in AllFiles:
        #     #print("item is", item, "\n")    
        #     foldername, LoDirs, LoFiles = item 

        #     for filename in LoFiles:
        #         if filename[-3:] == "csv" and (len(filename) == 10 or len(filename) == 11):    
        #             path = os.getcwd() + foldername + filename 
        #             df = pd.read_csv(path, engine='python', header=0, index_col=False)
        #             df_list.append(df)

        #         elif filename[-3:] == "csv" and "calculated_error" in filename:  
        #             path = os.getcwd() + foldername[1:] + "/" + filename 
        #             df = pd.read_csv(path, engine='python', header=None, index_col=False)
        #             delta_t_values = np.concatenate((delta_t_values, df.values[0][1:]))
        #             error_values = np.concatenate((error_values, df.values[3][1:]))
        
        final_df = pd.concat(df_list)

        # Plot using Seaborn
        sns.lmplot(x='Distance (m)', y='Signal Level (dB)', fit_reg=True, data=final_df, hue='Transmitter ID Number')
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.savefig("all_data_signal_plot.png")


        sns.lmplot(x='Distance (m)', y='Noise-Level (dB)', fit_reg = True, data=final_df, hue='Transmitter ID Number')
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.savefig('all_data_noise_plot.png')


        sns.lmplot(x='Distance (m)', y='Predicted Distance (m)', fit_reg = True, data=final_df, hue='Transmitter ID Number')
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.savefig('time_of_flight_distance_predictions_all_data.png')


        plt.hist(delta_t_values, self.NUM_OF_BINS)
        plt.title("Total Data: Times of Transmission")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency")
        plt.savefig("time_of_flight_total_histogram.png")
        plt.show()

        plt.hist(error_values, self.NUM_OF_BINS)
        plt.title("Total Data: Error")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency")
        plt.savefig("error_total_histogram.png")
        plt.show()

    def organize_files(self, foldername):
        os.mkdir(os.path.join(".", foldername))
        path = os.path.join(".", foldername)

        os.mkdir(os.path.join(path, "calculated_error_data"))
        os.mkdir(os.path.join(path, "delta_t_histograms"))
        os.mkdir(os.path.join(path, "noise_plots"))
        os.mkdir(os.path.join(path, "raw_data"))
        os.mkdir(os.path.join(path, "signal_plots"))
        os.mkdir(os.path.join(path, "summaries"))
        os.mkdir(os.path.join(path, "time_of_flight_histograms"))

        AllFiles = list(os.walk("."))  #Walks everything inside current directory

        _, _, LoFiles = AllFiles[0]


        for filename in LoFiles:
            if filename[-3:] == "csv" and "calculated_error" in filename:
                shutil.move(filename, os.path.join(path, "calculated_error_data"))
                
            elif filename[-3:] == "png" and "histogram" in filename:
                if "time_of_flight" in filename:
                    shutil.move(filename, os.path.join(path, "time_of_flight_histograms"))
                else:
                    shutil.move(filename, os.path.join(path, "delta_t_histograms"))
                    
            elif filename[-3:] == "csv" and "summaries" in filename:
                shutil.move(filename, os.path.join(path, "summaries"))
                
            elif filename[-3:] == "png" and "noise" in filename:
                shutil.move(filename, os.path.join(path, "noise_plots"))
                
            elif filename[-3:] == "png" and "signal" in filename:
                shutil.move(filename, os.path.join(path, "signal_plots"))
            
            elif filename[-3:] == "csv" and (len(filename) == 10 or len(filename) == 11):
                shutil.move(filename, os.path.join(path, "raw_data"))


if __name__ == '__main__':
    handler = Serial_Data_Handler()

    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()

    # consider this to make program more user-friendly. Otherwise, we will code in settings manually
    # TIME_TO_RUN, sensor_gps_coords, tag_gps_coords, distance = handler.get_settings()

    serial_port = handler.get_serial_data(ports, serialInst)
    #distance = handler.get_distance_from_gps_locations()
    distance = input("What's the distance?: ")

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
    data_list, summaries_list = handler.make_data_and_summaries_lists(output, distance)

    delta_t = handler.make_delta_t(data_list)
    # get std dev, statistics.stdev(sample_set, x_bar)
    std_dev_delta_t = statistics.stdev(delta_t[1:], statistics.mean(delta_t[1:]))
    print("Standard Deviation of sample is % s " % (std_dev_delta_t))

    handler.create_histogram(iteration, delta_t)

    # lists to get projected &  real tot & error between them
    predicted_times_of_transmission  = handler.get_predicted_times(delta_t)
    real_times_of_transmission  = handler.get_real_times(delta_t)
    error_tot = handler.get_error_tot(predicted_times_of_transmission, real_times_of_transmission)
    times_list = [delta_t, real_times_of_transmission, predicted_times_of_transmission, error_tot]

    # create csvs and plot
    handler.create_csvs(iteration, data_list, summaries_list, times_list)
    handler.create_plots(iteration)

    finished = input("Are you finished collecting data for the day? (Y or N): ")
    if finished == "Y" or finished == "YES" or finished == "y" or finished == "yes":
        foldername = input("What do you want to name the folder?: ")
        handler.create_final_plots()
        handler.organize_files(foldername)

