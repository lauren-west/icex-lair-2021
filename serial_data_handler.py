import csv
# from typing_extensions import final
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

    TIME_TO_RUN = 600 # seconds
    NUM_OF_BINS = 10 # Anywhere from 5-20 with 20 being with at least 1000 data points

    # allows user to input the temp., salinity, and depth the sensor is at when taking data
    # Temp = int(input("Temperature of the water in Celsius: "))
    # Salinity = int(input("Salinity of the water in ppt: "))
    # Depth = int(input("Depth of the sensor in m: "))

    # SPEED_OF_SOUND = 1449.2 + ((4.6)*Temp) - ((5.5*(10**-2))*(Temp**2)) + ((2.9*(10**(-4)))*(Temp**3)) \
    #     + ((1.34 - ((10**3)*Temp))*(Salinity - 35)) + ((1.6*(10**(-2)))*Depth) # average is 1500 m/s

    SPEED_OF_SOUND = 1460

    TAG_COORDINATES = (33.750672,-118.122642)
    SENSOR_COORDINATES = (33.752228,-118.12863)

    INTERNAL_CLOCK_TIMES = ["Internal Computer Clock"]

    FIRST_TIMESTAMP = None

    delta_t_avg = 8.17907142857143

    additive = 0
    adjustment_threshold = 0.0007


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
        data_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", \
            "Transmitter Code-Space", "Transmitter ID Number", "Signal Level (dB)", "Noise-Level (dB)", \
                'C', "Channel", "Tag GPS Coords", "Sensor GPS Coords", "Time (s)", "Distance (m)", "Time of Flight (s)", \
                    "Predicted Distance (m)"])

        summaries_list = []
        summaries_list.append(["Receiver Serial Number", "Three-Digit Line-Counter", "Date/Time", \
            "Scheduled Status (STS)", "Detection Count (DC)", "Ping Count (PC)", "Line Voltage (LV) [V]", \
                "Internal Receiver Temperature", "Detection Memory Used", "Raw Memory Used", "Tilt Information [G]", \
                     "Output Noise", "Output PPM Noise", "Tag GPS Coords", "Sensor GPS Coords", \
                         "Time (s)", "Distance (m)", "Time of Flight (s)", "Predicted Distance (m)"])
        
        # initial_time = None        # Used to calculate time elapsed
        counter = 0

        
        try:
            with open('data_1.csv', "r") as f:
                reader = csv.reader(f)
                _ = next(reader)
                row1 = next(reader)
                self.FIRST_TIMESTAMP = datetime.datetime.strptime(row1[2], '%Y-%m-%d %H:%M:%S.%f')
        except:
            line = output[0].split(',')
            line = [s[s.find("=")+1:].strip() for s in line]
            self.FIRST_TIMESTAMP = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S.%f')


        for line in output:
            
            line = line.split(',')
            line = [s[s.find("=")+1:].strip() for s in line]
            
            if len(line) > 12:
                summaries_list.append(line)
            else:
                data_list.append(line)
            
        
        for line in data_list[1:]:
            current_index = data_list.index(line)
            line.append(self.TAG_COORDINATES)   #Adds tag coords for now
            line.append(self.SENSOR_COORDINATES)   #Adds sensor coords for now

            current_datetime = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S.%f')

            diff_in_time = (current_datetime - self.FIRST_TIMESTAMP).total_seconds()
            time_of_flight = diff_in_time % self.delta_t_avg

            if time_of_flight > 8:
                time_of_flight = self.delta_t_avg - time_of_flight

            if current_index > 2:
                previous_line = data_list[current_index - 1]
                previous_time_of_flight = float(previous_line[-2])

                diff_time_of_flight = time_of_flight - previous_time_of_flight
                if diff_time_of_flight > self.adjustment_threshold:
                    self.additive = diff_time_of_flight
                    revised_initial_time = self.FIRST_TIMESTAMP + datetime.timedelta(0, handler.additive)
                    print("We are at timestamp: ", current_datetime)
                    print("\nBefore:", self.FIRST_TIMESTAMP)
                    self.FIRST_TIMESTAMP = revised_initial_time
                    print("After:", self.FIRST_TIMESTAMP, "\n")

            line.append(diff_in_time)
            line.append(distance)
            line.append(time_of_flight)
            line.append(time_of_flight * self.SPEED_OF_SOUND) # Predicted Distance

            for s in line:
                try:
                    s = float(s)
                except:
                    pass  
        
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
            current_datetime = datetime.datetime.strptime(data_list[i][2], '%Y-%m-%d %H:%M:%S.%f')
            total_seconds = (current_datetime - past_datetime).total_seconds()
            delta_t.append(total_seconds)

            # if (current_datetime - past_datetime).total_seconds() > 10:
            #     pass
            # else:
            #     total_seconds = (current_datetime - past_datetime).total_seconds()
            #     delta_t.append(total_seconds)
        return delta_t

    def create_histogram(self, iteration, delta_t):
        """ 
            Creates and saves histogram in file
        """
        no_outlier = []
        for time in delta_t[1:]:
            if time < 10:
                no_outlier.append(time)
        delta_t_np = np.array(no_outlier)

        NUM_OF_BINS = 10 # Anywhere from 5-20 with 20 being with at least 1000 data points
        plt.hist(delta_t_np, NUM_OF_BINS)
        plt.title("Time of Transmission Histogram")
        plt.xlabel("Difference in Time of Pings (s)")
        plt.ylabel("Frequency")
        plt.savefig(iteration + "_histogram.png")
        plt.close()

    def get_predicted_times(self, delta_t):
        """ Returns:
          predicted_times_of_transmission (list): contains doubles, each predicted 
          time calculated by using an average tot (average delta_t) before drift.
          t_predicted = t0 + (k * self.delta_t_avg)

          Note: there may be a better way to get self.delta_t_avg than the method below
        """
        predicted_times_of_transmission = ["Predicted Times of Transmission"]
        t0 = 0

        # dilemma: What should delta t avg be?
        # self.delta_t_avg  = sum(delta_t[1:]) / (len(delta_t) - 1)
        # self.delta_t_avg  = sum(delta_t[1:10]) / (len(delta_t[1:10]))

        print("avg: ", self.delta_t_avg)
        
        for i in range(1, len(delta_t)):
            predicted_times_of_transmission.append(t0 + i * self.delta_t_avg)

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
        # value // 8.17907  == 2,   value == diff between real and predicted
        # error = time_of_flight / value  == 0.01
        error_tot = ["Error"]
        
        for i in range(1, len(predicted_times_of_transmission)):
            difference = real_times_of_transmission[i] - predicted_times_of_transmission[i]
            if difference > 8:
                integer_divide_value = difference//self.delta_t_avg
                time_of_flight = difference % self.delta_t_avg
                if integer_divide_value > 0:
                    error = time_of_flight/integer_divide_value
                else:
                    error = time_of_flight
                error_tot.append(error)
            else:
                error_tot.append(difference)

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

        #df = df.dropna()
        #df_clean = df
        
        # Plot using Seaborn
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        #     print(df)

        sns.lmplot(x='Time (s)', y='Signal Level (dB)', fit_reg=True, data=df, hue='Transmitter ID Number')
        
        # Tweak these limits
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.title("Signal Level over Time at One Distance")
        plt.xlabel("Time (s)")
        plt.ylabel("Signal Level (dB)")
        plt.savefig(iteration + "_signal_plot.png")
        plt.close()

        # Plot using Seaborn
        sns.lmplot(x='Time (s)', y='Noise-Level (dB)', fit_reg = True, data=df, hue='Transmitter ID Number')
        
        # Tweak these limits
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.title("Noise Level over Time at One Distance")
        plt.xlabel("Time (s)")
        plt.ylabel("Noise-Level (dB)")
        plt.savefig(iteration + '_noise_plot.png')
        plt.close()

        self.create_plots_without_noise_signal(iteration)

        # plt.hist(df['Time of Flight (s)'], self.NUM_OF_BINS)
        # plt.title("Time of Flight")
        # plt.xlabel("Time (s)")
        # plt.ylabel("Frequency")
        # plt.savefig("time_of_flight_" + iteration + ".png")
        # plt.close()

        # plt.hist(df['Predicted Distance (m)'], self.NUM_OF_BINS)
        # plt.title("Distance Predictions")
        # plt.xlabel("Distance (m)")
        # plt.ylabel("Frequency")
        # plt.savefig("time_of_flight_distance_predictions_" + iteration + ".png")
        # plt.close()
    
    def create_plots_without_noise_signal(self, iteration):
        # Read in the data
        # 
        # for read_csv, use header=0 when row 0 is a header row 

        filename = iteration + '.csv'
        df = pd.read_csv(filename, header=0, index_col=False)   # read the file w/header row #0
        # print(f"{filename} : file read into a pandas dataframe.")

        plt.hist(df['Time of Flight (s)'], self.NUM_OF_BINS)
        plt.title("Time of Flight")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency")
        plt.savefig("time_of_flight_" + iteration + ".png")
        plt.close()

        plt.hist(df['Predicted Distance (m)'], self.NUM_OF_BINS)
        plt.title("Distance Predictions")
        plt.xlabel("Distance (m)")
        plt.ylabel("Frequency")
        plt.savefig("time_of_flight_distance_predictions_" + iteration + ".png")
        plt.close()
    

    def create_final_plots(self):
        AllFiles = list(os.walk("."))  #Walks everything inside current directory

        df_list = []
        data_file_list = []
        delta_t_values = np.array([])
        error_values = np.array([])

        _, _, LoFiles = AllFiles[0] 

        for filename in LoFiles:
            if filename[-3:] == "csv" and (len(filename) == 10 or len(filename) == 11):    
                path = os.getcwd() + "/" + filename
                data_file_list.append(filename)
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
        plt.title("Signal Level over Distance")
        plt.savefig("all_data_signal_plot.png")
        plt.close()


        sns.lmplot(x='Distance (m)', y='Noise-Level (dB)', fit_reg = True, data=final_df, hue='Transmitter ID Number')
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.title("Noise Level over Distance")
        plt.savefig('all_data_noise_plot.png')
        plt.close()

        self.create_final_plots_without_noise_signal(final_df = final_df, delta_t_values = delta_t_values, error_values = error_values, data_file_list = data_file_list)

    def create_final_plots_without_noise_signal(self, final_df = None, delta_t_values = None, error_values = None, data_file_list = []):
        if final_df is None or delta_t_values is None or error_values is None:
            AllFiles = list(os.walk("."))  #Walks everything inside current directory

            df_list = []
            delta_t_values = np.array([])
            error_values = np.array([])

            _, _, LoFiles = AllFiles[0] 
            print(LoFiles)
            for filename in LoFiles:
                if filename[-3:] == "csv" and (len(filename) == 10 or len(filename) == 11):    
                    path = os.getcwd() + "/" + filename 
                    data_file_list.append(filename)
                    df = pd.read_csv(path, engine='python', header=0, index_col=False)
                    df_list.append(df)

                elif filename[-3:] == "csv" and "calculated_error" in filename:  
                    path = os.getcwd() + "/" + filename 
                    df = pd.read_csv(path, engine='python', header=None, index_col=False)
                    delta_t_values = np.concatenate((delta_t_values, df.values[0][1:]))
                    error_values = np.concatenate((error_values, df.values[3][1:]))
            
            final_df = pd.concat(df_list)

        # sns.lmplot(x='Distance (m)', y='Predicted Distance (m)', fit_reg = True, data=final_df, hue='Transmitter ID Number')
        plt.scatter(final_df['Distance (m)'], final_df['Predicted Distance (m)'])
        plt.ylim(None, None)
        plt.xlim(None, None)
        plt.title("Actual Distance versus Predicted Distance")
        plt.xlabel("Actual Distance (m)")
        plt.ylabel("Predicted Distance (m)")
        plt.savefig('time_of_flight_distance_predictions_all_data.png')
        plt.close()

        plt.hist(delta_t_values, self.NUM_OF_BINS)
        plt.title("Total Data: Times of Transmission")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency")
        plt.savefig("time_of_flight_total_histogram.png")
        plt.close()

        plt.hist(error_values, self.NUM_OF_BINS)
        plt.title("Total Data: Error")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency")
        plt.savefig("error_total_histogram.png")
        plt.close()

        self.create_step_plots(data_file_list)

    def create_step_plots(self, file_list):
        # AllFiles = list(os.walk("./" + foldername))
        # path, _, LoFiles = AllFiles[4]
        file_list.sort()
        time_diffs = []
        distances = []
        num_ticks = []
        first_datapoint = True
        time_zero = None
        timestamp_0 = None
        tof = []
        distances_and_tof = []

        for file in file_list:
            csv_path = os.path.join(".", file)
            df = pd.read_csv(csv_path, engine='python', header=0, index_col=False)

            if first_datapoint:
                time_zero = df["Date/Time"][0]
                timestamp_0 = datetime.datetime.strptime(time_zero, '%Y-%m-%d %H:%M:%S.%f')
            num_ticks.append(len(df["Distance (m)"]))
            # distances.append(df["Distance (m)"][0])
            # tof.append(df["Time of Flight (s)"])
            distances_and_tof.append((df["Distance (m)"][0], df["Time of Flight (s)"]))
            
            for current_datetime in df["Date/Time"]:
                timestamp_x = datetime.datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S.%f')
                time_diffs.append((timestamp_x - timestamp_0).total_seconds())
        
        distances_and_tof.sort(key=lambda pair: pair[0])
        distances = [dist[0] for dist in distances_and_tof]
        tof = [tof[1] for tof in distances_and_tof]
        try:
            distances.append(abs(distances[-1] - distances[-2]) + distances[-1])
        except:
            distances.append(distances[0] * 2)  

        x_plot = []

        for i in range(0, len(distances)-1):
            x_plot.append(np.linspace(distances[i], distances[i+1], num_ticks[i]))
            
        x_plot = np.concatenate(x_plot)
        tof = np.concatenate(tof)

        plt.plot(x_plot, time_diffs) 
        plt.title("Time Difference vs Time Elapsed")
        plt.xlabel("Time (s)")
        plt.ylabel("Time Difference (s)")
        plt.savefig("time_diff_vs_elasped_step_plot.png")
        plt.close()

        N = [i/self.delta_t_avg for i in time_diffs]
        # m = [i%self.delta_t_avg for i in time_diffs]
        m = tof

        value_list = []

        for value in m:
            if value < 8:
                value_list.append(value)
            else:
                value_list.append(self.delta_t_avg - value)

        m = value_list

        multiplied = [i * 1460 for i in m]

        plt.plot(x_plot, N) 
        plt.title("N vs Distance")
        plt.xlabel("Distance (m)")
        plt.ylabel("N")
        plt.savefig("n_vs_distance_step_plot.png")
        plt.close()

        plt.plot(x_plot, m) 
        plt.title("Mod vs Distance")
        plt.xlabel("Distance (m)")
        plt.ylabel("Mod")
        #plt.xlim([0,3])
        plt.savefig("mod_vs_distance_step_plot.png")
        plt.close()

        # predicted_dist_per_sec = 0.02367587849280499

        # time_diffs_changed = [i * predicted_dist_per_sec for i in time_diffs]
        # z = [a - b for a, b in zip(multiplied, time_diffs_changed)]

        plt.plot(x_plot, multiplied) 
        plt.title("Predicted Distance vs Distance")
        plt.xlabel("Distance (m)")
        plt.ylabel("Predicted Distance (m)")
        #plt.xlim([0,3])
        plt.savefig("predicted_dist_vs_actual_dist_step_plot.png")
        plt.close()


    def organize_files(self, foldername):
        os.mkdir(os.path.join(".", foldername))
        path = os.path.join(".", foldername)

        os.mkdir(os.path.join(path, "calculated_error_data"))
        os.mkdir(os.path.join(path, "delta_t_histograms"))
        os.mkdir(os.path.join(path, "noise_plots"))
        os.mkdir(os.path.join(path, "raw_data"))
        os.mkdir(os.path.join(path, "signal_plots"))
        os.mkdir(os.path.join(path, "step_plots"))
        os.mkdir(os.path.join(path, "summaries"))
        os.mkdir(os.path.join(path, "time_of_flight_plots"))

        AllFiles = list(os.walk("."))  #Walks everything inside current directory

        _, _, LoFiles = AllFiles[0]


        for filename in LoFiles:
            if filename[-3:] == "csv" and "calculated_error" in filename:
                shutil.move(filename, os.path.join(path, "calculated_error_data"))

            elif filename[-3:] == "png" and "time_of_flight" in filename:
                shutil.move(filename, os.path.join(path, "time_of_flight_plots"))

            elif filename[-3:] == "png" and "histogram" in filename:
                shutil.move(filename, os.path.join(path, "delta_t_histograms"))
                    
            elif filename[-3:] == "csv" and "summaries" in filename:
                shutil.move(filename, os.path.join(path, "summaries"))
                
            elif filename[-3:] == "png" and "noise" in filename:
                shutil.move(filename, os.path.join(path, "noise_plots"))
                
            elif filename[-3:] == "png" and "signal" in filename:
                shutil.move(filename, os.path.join(path, "signal_plots"))
            
            elif filename[-3:] == "png" and "step_plot" in filename:
                shutil.move(filename, os.path.join(path, "step_plots"))
            # elif filename[-3:] == "csv" and (len(filename) == 10 or len(filename) == 11):
            elif filename[-3:] == "csv":
                shutil.move(filename, os.path.join(path, "raw_data"))


# consider this to make program more user-friendly. Otherwise, we will code in settings manually
# TIME_TO_RUN, sensor_gps_coords, tag_gps_coords, distance = handler.get_settings()
def run_program_with_new_data(handler):

    ports = serial.tools.list_ports.comports()
    serialInst = serial.Serial()
    handler.get_serial_data(ports, serialInst)
    #distance = handler.get_distance_from_gps_locations()
    distance = input("What's the distance?: ")

    iteration = "data_" + str(input("Iteration of data collection (Enter a number to not overwrite files): "))
    
    output = []

    #Starts the stopwatch/counter
    t1_start = time.perf_counter()

    with open("raw_serial_" + iteration + ".csv", "w") as f:
        writer = csv.writer(f)
        while time.perf_counter() - t1_start < handler.TIME_TO_RUN:
            if serialInst.in_waiting:
                packet = serialInst.readline()
                time_elapsed = time.perf_counter()-t1_start
                handler.INTERNAL_CLOCK_TIMES.append(time_elapsed)
                print(packet.decode('utf').rstrip('\n'))
                output.append(packet.decode('utf').rstrip('\n'))

                row = output[-1]
                line = row.split(',')
                line = [s[s.find("=")+1:].strip() for s in line]
                line.append(time_elapsed)
                writer.writerow(line)


    # data_list is 2D array of strings of data
    # rows are lines, and cols are the specific measurements
    data_list, summaries_list = handler.make_data_and_summaries_lists(output, distance)
    delta_t = handler.make_delta_t(data_list)

    # get std dev, statistics.stdev(sample_set, x_bar)
    std_dev_delta_t = statistics.stdev(delta_t[1:], statistics.mean(delta_t[1:]))
    print("Standard Deviation of sample's delta_t is % s " % (std_dev_delta_t))

    handler.create_histogram(iteration, delta_t)

    # lists to get projected &  real tot & error between them
    predicted_times_of_transmission  = handler.get_predicted_times(delta_t)
    real_times_of_transmission  = handler.get_real_times(delta_t)
    error_tot = handler.get_error_tot(predicted_times_of_transmission, real_times_of_transmission)
    times_list = [delta_t, real_times_of_transmission, predicted_times_of_transmission, error_tot, handler.INTERNAL_CLOCK_TIMES]

    # create csvs and plot
    handler.create_csvs(iteration, data_list, summaries_list, times_list)
    handler.create_plots(iteration)

    finished = input("Are you finished collecting data for the day? (Y or N): ")
    if finished == "Y" or finished == "YES" or finished == "y" or finished == "yes":
        foldername = input("What do you want to name the folder?: ")
        handler.create_final_plots()
        handler.organize_files(foldername)


def run_program_with_old_data(handler):
    # name_of_folder = "Some String"
    foldername = input("What is the name of the folder of data you want to use? (Case sensitive): ")
    path = os.path.join(".", foldername)
    AllFiles = list(os.walk(path))
    path, _, LoFiles = AllFiles[4]    # Accesses the raw data from the dataset
    LoFiles.sort()
    counter = 0    # Used to make sure we can get handler.FIRST_TIMESTAMP
    index_of_first_raw_data = len(LoFiles)
    new_dataset = ("raw_serial_data_1.csv") in LoFiles      # Older Datasets do not contain raw serial data

    if new_dataset:
        index_of_first_raw_data = LoFiles.index("raw_serial_data_1.csv")

    true_first_time_stamp = None

    for file in LoFiles[:index_of_first_raw_data]:
        if file == ".DS_Store":
            continue
        
        df = pd.read_csv(path + "/" + file, engine='python', header=0, index_col=False)
        new_time_of_flight_list = []
        new_predicted_distance_list = []
        handler.FIRST_TIMESTAMP = true_first_time_stamp
        # print("Timestamp:", handler.FIRST_TIMESTAMP, " Using  File: ", file)

        for line in df.values:
            current_datetime = datetime.datetime.strptime(line[2], '%Y-%m-%d %H:%M:%S.%f')

            if counter == 0:
                true_first_time_stamp = current_datetime
                handler.FIRST_TIMESTAMP = true_first_time_stamp
                counter += 1

            diff_in_time = (current_datetime - handler.FIRST_TIMESTAMP).total_seconds()
            time_of_flight = diff_in_time % handler.delta_t_avg

            if time_of_flight > 8:
                time_of_flight = handler.delta_t_avg - time_of_flight

            current_index = np.where(df.values == line)[0][0]

            if current_index > 1:   # First TOF seems to almost always be 0
                previous_line = df.values[current_index -1]
                previous_time_of_flight = previous_line[-2]

                diff_time_of_flight = time_of_flight - previous_time_of_flight
                if diff_time_of_flight > handler.adjustment_threshold:
                    handler.additive = diff_time_of_flight
                    revised_initial_time = handler.FIRST_TIMESTAMP + datetime.timedelta(0, handler.additive)
                    print("\nBefore:", handler.FIRST_TIMESTAMP)
                    handler.FIRST_TIMESTAMP = revised_initial_time
                    print("After:", handler.FIRST_TIMESTAMP, "\n")
            
            new_time_of_flight_list.append(time_of_flight)
            new_predicted_distance_list.append(time_of_flight * handler.SPEED_OF_SOUND)
        
        df['Time of Flight (s)'] = new_time_of_flight_list
        df['Predicted Distance (m)'] = new_predicted_distance_list
        data_list = df.values

        df.to_csv(file, index=False)

        delta_t = handler.make_delta_t(data_list)

        # get std dev, statistics.stdev(sample_set, x_bar)
        std_dev_delta_t = statistics.stdev(delta_t[1:], statistics.mean(delta_t[1:]))
        print("Standard Deviation of sample's delta_t is % s " % (std_dev_delta_t))

        handler.create_histogram(file[:-4], delta_t)

        # lists to get projected &  real tot & error between them
        predicted_times_of_transmission  = handler.get_predicted_times(delta_t)
        real_times_of_transmission  = handler.get_real_times(delta_t)
        error_tot = handler.get_error_tot(predicted_times_of_transmission, real_times_of_transmission)

        clock_times = []

        if new_dataset:
            datafile = open(path + '/raw_serial_' + file, 'r')
            datareader = csv.reader(datafile, delimiter=',')
            for row in datareader:
                if row == []:
                    pass
                else:
                    clock_times.append(row[-1])    

        times_list = [delta_t, real_times_of_transmission, predicted_times_of_transmission, error_tot, clock_times]

        # create csvs and plot
        with open(file[:-4] + "_calculated_error_values.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(times_list)

        if new_dataset:
            handler.create_plots(file[:-4])
        else:
            handler.create_plots_without_noise_signal(file[:-4])

    foldername = input("What do you want to name the folder? (DO NOT REPEAT OLD DATASET NAME): ")
    
    if new_dataset:
        handler.create_final_plots()
    else:
        handler.create_final_plots_without_noise_signal()
        
    handler.organize_files(foldername)


if __name__ == '__main__':
    handler = Serial_Data_Handler()

    which_data = input("Are you collecting new data or using old data? (Enter new or old): ")

    if which_data.lower() ==  "new":
        run_program_with_new_data(handler)
    elif which_data.lower() == "old":
        run_program_with_old_data(handler)
    else:
        print("Invalid Input. Please rerun the program and try again.")
