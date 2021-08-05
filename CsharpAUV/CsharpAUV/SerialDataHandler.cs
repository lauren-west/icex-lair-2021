using System;
using System.IO;
using System.IO.Ports;
using System.Collections.Generic;
using System.Collections;
using System.Diagnostics;
using System.Linq;

namespace CsharpAUV
{
    class SerialDataHandler
    {
        static SerialPort _serialPort;
        double speedOfSound;
        bool firstLiveDateTime = true;
        DateTime firstLiveDateTimeVal;
        string filename1;
        string filename2;
        public List<string> file1List;
        public List<string> file2List;
        int file1ListIndexPointer;
        int file2ListIndexPointer;

        double allowableTimeLapse = 4.0;

        List<Tuple<double, DateTime, int, int>> outputToParticleFilter = new List<Tuple<double, DateTime, int, int>>();

        public SerialDataHandler()
        {
            // empty constructor for live serial data
        }

        public SerialDataHandler(String file1, String file2)
        {
            filename1 = file1;
            filename2 = file2;
            file1List = this.getFileList(file1);
            file2List = this.getFileList(file2);
            file1ListIndexPointer = 0;
            file2ListIndexPointer = 0;
        }

        public List<string> getFileList(string filename) {
            List<string> csvLines = new List<string>();
            using (var reader = new StreamReader(@"../../../" + filename + ".csv"))
            {
                string headerLine = reader.ReadLine();

                while (!reader.EndOfStream)
                {
                    var line = reader.ReadLine();
                    var values = line.Split(';');

                    if (!String.IsNullOrEmpty(line)) {
                        csvLines.Add(line);
                    }
                }
            }

            return csvLines;
        }

        public List<Tuple<double, DateTime, int, int>> getMeasurements1(DateTime currentTimeFromSimulator)
        {
            this.speedOfSound = 1460;
            bool found1 = false;
            bool found2 = false;
            List<Tuple<double, DateTime, int, int>> outputToSimulator = new List<Tuple<double, DateTime, int, int>>();
            DateTime pointer1dt = this.getDateTimeFromMessage(file1List[this.file1ListIndexPointer]);
            DateTime pointer2dt = this.getDateTimeFromMessage(file2List[this.file2ListIndexPointer]);

            while (!found1 || !found2)
            {
                // equivalent logic for file1
                if (pointer1dt > currentTimeFromSimulator && Math.Abs((pointer1dt - currentTimeFromSimulator).TotalSeconds) > this.allowableTimeLapse)
                {
                    found1 = true;
                }
                else if (pointer1dt <= currentTimeFromSimulator && Math.Abs((pointer1dt - currentTimeFromSimulator).TotalSeconds) < this.allowableTimeLapse)
                {
                    outputToSimulator.Add(this.isolateInfoFromMessages(1, file1List[this.file1ListIndexPointer]));
                    found1 = true;
                }
                else
                {
                    if (this.file1ListIndexPointer < this.file1List.Count - 1)
                    {
                        if (this.getDateTimeFromMessage(file1List[this.file1ListIndexPointer + 1]) <= currentTimeFromSimulator)
                        {
                            this.file1ListIndexPointer = this.file1ListIndexPointer + 1;
                            pointer1dt = this.getDateTimeFromMessage(file1List[this.file1ListIndexPointer]);
                        }
                        found1 = true;
                        outputToSimulator.Add(this.isolateInfoFromMessages(1, file1List[this.file1ListIndexPointer]));
                    }
                    else
                    {
                        found1 = true;
                    }

                }
                // equivalent logic for file2
                if (pointer2dt > currentTimeFromSimulator && Math.Abs((pointer2dt - currentTimeFromSimulator).TotalSeconds) > this.allowableTimeLapse)
                { 
                    found2 = true;
                }
                else if (pointer2dt <= currentTimeFromSimulator && Math.Abs((pointer2dt - currentTimeFromSimulator).TotalSeconds) < this.allowableTimeLapse)
                {
                    outputToSimulator.Add(this.isolateInfoFromMessages(2, file2List[this.file2ListIndexPointer]));
                    found2 = true;
                }
                else
                {
                    if (this.file2ListIndexPointer < this.file2List.Count - 1)
                    {
                        if (this.getDateTimeFromMessage(file2List[this.file2ListIndexPointer + 1]) <= currentTimeFromSimulator) {
                            this.file2ListIndexPointer = this.file2ListIndexPointer + 1;
                            pointer2dt = this.getDateTimeFromMessage(file2List[this.file2ListIndexPointer]);
                        }
                        found2 = true;
                        outputToSimulator.Add(this.isolateInfoFromMessages(2, file2List[this.file2ListIndexPointer]));
                    }
                    else
                    {
                        found2 = true;
                    }

                }
            }

            return outputToSimulator;
        }

        public DateTime getInitialTime1()
        {
            string firstline1 = this.file1List[0];
            string firstline2 = this.file2List[0];
            DateTime d1 = this.getDateTimeFromMessage(firstline1);
            DateTime d2 = this.getDateTimeFromMessage(firstline2);
            if (d1 < d2)
            {
                return d1;
            }
            return d2;
        }

        public DateTime getFinalTime1()
        {
            string lastline1 = this.file1List[this.file1List.Count - 1];
            string lastline2 = this.file2List[this.file1List.Count - 1];
            DateTime d1 = this.getDateTimeFromMessage(lastline1);
            DateTime d2 = this.getDateTimeFromMessage(lastline2);

            if (d1 > d2)
            {
                return d1;
            }
            return d2;
        }

        public Tuple<double, DateTime, int, int> getLiveMeasurements()
        {
            string message = "";
            Tuple<double, DateTime, int, int> outputToPF = Tuple.Create(0.0,new DateTime(), 0, 0);

            _serialPort = new SerialPort();
            _serialPort.PortName = SetPortName(_serialPort.PortName);
            _serialPort.ReadTimeout = 500;
            _serialPort.WriteTimeout = 500;

            Console.WriteLine("Beginning to listen to " + _serialPort.PortName + ".");

            _serialPort.Open();

            Stopwatch sw = new Stopwatch();
            sw.Start();

            while (sw.ElapsedMilliseconds < 40) // give 40 ms to listen into serial port for data --> check this with Clark...
            {
                try
                {
                    message = _serialPort.ReadLine();
                    //serialdatahandler.rawSerialData.Add(message);
                    if (message != null)
                    {
                        Tuple<double, DateTime, int, int> data = this.isolateInfoFromMessages(0, message);
                        // retrieve first datetime (this only happens once per run!!)
                        if (this.firstLiveDateTime)
                        {
                            this.firstLiveDateTimeVal = data.Item2;
                            this.firstLiveDateTime = false;
                        }

                        outputToPF = Tuple.Create(data.Item1, data.Item2, data.Item3, data.Item4);
                        return outputToPF;
                    }
                }
                catch (TimeoutException) { }
            }
            _serialPort.Close();
            return outputToPF;
        }

        public double calcDistFromTOF(double tof)
        {  /* getting predicted distance from TOF
            * 
            * param: (double) timeOfFlight 
            * returns: (double) distances
            */
            return this.speedOfSound * tof;
        }

        public double makeTimeOfFlight(int file, DateTime dateTimeCurrent)
        {   /* 
             * param: sensor 0, 1, or 2
             * 0 means live serial date,
             * 1 means csv sensor 1
             * 2 means csv sensor2
             * returns: timeOfFlight
             */
            double tof;
            if (file == 1)
            {
                double diff1 = dateTimeCurrent.Subtract(this.getDateTimeFromMessage(this.file1List[0])).TotalSeconds;
                tof = diff1 % 8.179;
            }
            else if (file == 2)
            {
                double diff2 = dateTimeCurrent.Subtract(this.getDateTimeFromMessage(this.file2List[0])).TotalSeconds;
                tof = diff2 % 8.179; ;
            }
            else {
                // live stuff
                double diff1 = dateTimeCurrent.Subtract(this.firstLiveDateTimeVal).TotalSeconds;
                tof = diff1 % 8.179;
            }

            if (tof > 8)
            {
                tof = 8.179 - tof;
            }
            return tof;

        }

        public DateTime getDateTimeFromMessage(string message)
        {   /* 
             * Using raw serial data, we isolate dateTimes and transmitterIDs
             * 
             * returns: dateTime, transmitterID, and sensor id
             */
            string[] tempArr = message.Split(',');
            return DateTime.Parse(tempArr[2]);
        }

        public Tuple<double, DateTime, int, int> isolateInfoFromMessages(int filenum, string message)
        {   /* 
             * Using raw serial data, we isolate dateTimes and transmitterIDs
             * 
             * returns: dateTime, transmitterID, and sensor id
             */
            string[] tempArr = message.Split(',');

            DateTime dateTime = DateTime.Parse(tempArr[2]); //DateTimeOffset.Parse(tempArr[2]).UtcDateTime;
            string transmitterID = tempArr[4];
            string sensorID = tempArr[0];

            Console.WriteLine(message);
            double tof1 = this.makeTimeOfFlight(filenum, dateTime);
            double distance = this.calcDistFromTOF(tof1);

            return Tuple.Create(distance, dateTime, Convert.ToInt32(transmitterID), Convert.ToInt32(sensorID));
        }

        public double calcSpeedOfSound()
        {
            /* 
             * Prompts salinity, temperature, and depth quantities
             * 
             * returns: speed of sound
             */

            Console.WriteLine("Enter temperature (Celsius): Default=12");
            double temp = Convert.ToDouble(Console.ReadLine());
            Console.WriteLine("Enter depth (meters): Default=10");
            double depth = Convert.ToDouble(Console.ReadLine()); ;
            Console.WriteLine("Enter salinity (ppt): Default=33.5");
            double salinity = Convert.ToDouble(Console.ReadLine());

            // the mackenzie equation for speed of sound underwater
            // http://resource.npl.co.uk/acoustics/techguides/soundseawater/content.html

            double speedOfSound = 1448.96 + (4.591 * temp) -
                (5.304 * Math.Pow(10, -2) * Math.Pow(temp, 2)) +
                (2.374 * Math.Pow(10, -4) * Math.Pow(temp, 3)) +
                (1.340 * (salinity - 35)) + (1.630 * Math.Pow(10, -2) * depth) +
                (1.675 * Math.Pow(10, -7) * Math.Pow(depth, 2)) -
                (1.025 * Math.Pow(10, -2) * temp * (salinity - 35)) -
                (7.139 * Math.Pow(10, -13) * temp * Math.Pow(depth, 3));

            return speedOfSound;
        }

        public Boolean runCSV()
        {
            Console.WriteLine("Would you like to run old data from a CSV? Respond with Y or N");
            string yesno = (Console.ReadLine());
            if (yesno == "Y")
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        public int getTimeToRun()
        {   /* 
             * Prompts for a time to run in minutes,
             * 
             * returns: time to run in milliseconds
             */

            Console.WriteLine("Enter time to run program (minutes): ");
            int timeToRun = int.Parse(Console.ReadLine());

            // convert minutes to milliseconds
            timeToRun = 60000 * timeToRun;

            return timeToRun;
        }

        // Display Port values and prompt user to enter a port.
        public static string SetPortName(string defaultPortName)
        {
            string portName;

            Console.WriteLine("Available Ports:");
            foreach (string s in SerialPort.GetPortNames())
            {
                Console.WriteLine("   {0}", s);
            }

            Console.Write("Enter COM port value (Default: {0}): ", defaultPortName);
            portName = Console.ReadLine();

            if (portName == "" || !(portName.ToLower()).StartsWith("com"))
            {
                portName = defaultPortName;
            }
            return portName;
        }
        // Display BaudRate values and prompt user to enter a value.
        public static int SetPortBaudRate(int defaultPortBaudRate)
        {
            string baudRate;

            Console.Write("Baud Rate(default:{0}): ", defaultPortBaudRate);
            baudRate = Console.ReadLine();

            if (baudRate == "")
            {
                baudRate = defaultPortBaudRate.ToString();
            }

            return int.Parse(baudRate);
        }
        // Display PortParity values and prompt user to enter a value.
        public static Parity SetPortParity(Parity defaultPortParity)
        {
            string parity;

            Console.WriteLine("Available Parity options:");
            foreach (string s in Enum.GetNames(typeof(Parity)))
            {
                Console.WriteLine("   {0}", s);
            }

            Console.Write("Enter Parity value (Default: {0}):", defaultPortParity.ToString(), true);
            parity = Console.ReadLine();

            if (parity == "")
            {
                parity = defaultPortParity.ToString();
            }

            return (Parity)Enum.Parse(typeof(Parity), parity, true);
        }

        // Display DataBits values and prompt user to enter a value.
        public static int SetPortDataBits(int defaultPortDataBits)
        {
            string dataBits;

            Console.Write("Enter DataBits value (Default: {0}): ", defaultPortDataBits);
            dataBits = Console.ReadLine();

            if (dataBits == "")
            {
                dataBits = defaultPortDataBits.ToString();
            }

            return int.Parse(dataBits.ToUpperInvariant());
        }

        // Display StopBits values and prompt user to enter a value.
        public static StopBits SetPortStopBits(StopBits defaultPortStopBits)
        {
            string stopBits;

            Console.WriteLine("Available StopBits options:");
            foreach (string s in Enum.GetNames(typeof(StopBits)))
            {
                Console.WriteLine("   {0}", s);
            }

            Console.Write("Enter StopBits value (None is not supported and \n" +
             "raises an ArgumentOutOfRangeException. \n (Default: {0}):", defaultPortStopBits.ToString());
            stopBits = Console.ReadLine();

            if (stopBits == "")
            {
                stopBits = defaultPortStopBits.ToString();
            }

            return (StopBits)Enum.Parse(typeof(StopBits), stopBits, true);
        }

        public static Handshake SetPortHandshake(Handshake defaultPortHandshake)
        {
            string handshake;

            Console.WriteLine("Available Handshake options:");
            foreach (string s in Enum.GetNames(typeof(Handshake)))
            {
                Console.WriteLine("   {0}", s);
            }

            Console.Write("Enter Handshake value (Default: {0}):", defaultPortHandshake.ToString());
            handshake = Console.ReadLine();

            if (handshake == "")
            {
                handshake = defaultPortHandshake.ToString();
            }

            return (Handshake)Enum.Parse(typeof(Handshake), handshake, true);
        }
    }
}