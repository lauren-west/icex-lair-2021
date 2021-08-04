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
        int timeToRun;
        bool firstLiveDateTime = true;
        DateTime firstLiveDateTimeVal;
        DateTime firstDateTimeVal1;
        DateTime firstDateTimeVal2;
        string filename1;
        string filename2;
        double allowableTimeLapse = 4.2;
        public bool _continue = true;

        List<Tuple<double, DateTime, int, int>> outputToParticleFilter = new List<Tuple<double, DateTime, int, int>>();

        public SerialDataHandler()
        {
            // empty constructor for live serial data
        }

        public SerialDataHandler(String file1, String file2)
        {
            filename1 = file1;
            filename2 = file2;
        }
        
        public List<Tuple<double, DateTime, int, int>> getMeasurements(DateTime startTimeFromSimulator)
        {
            this.speedOfSound = 1460;
            List<Tuple<double, DateTime, int, int>> outputToSimulator = new List<Tuple<double, DateTime, int, int>>();

            using (StreamReader sr = new StreamReader(@"../../../" + this.filename1 + ".csv"))
            {
                using (StreamReader sr2 = new StreamReader(@"../../../" + this.filename2 + ".csv"))
                {
                    string headerLine = sr.ReadLine();
                    string headerLine2 = sr2.ReadLine();
                    double tof1, tof2;
                    double distance1 = -1.0;
                    double distance2 = -1.0;
                    bool read_message1 = true;
                    bool read_message2 = true;
                    string message1 = "";
                    string message2 = "";
                    bool end1 = false;
                    bool end2 = false;

                    Tuple<DateTime, int, int> data1 = Tuple.Create(new DateTime(), 0, 0);
                    Tuple<DateTime, int, int> data2 = Tuple.Create(new DateTime(), 0, 0);
                    
                    while (read_message1 || read_message2)
                    {
                        if (sr.EndOfStream)
                        {
                            read_message1 = false;
                            end1 = false;
                        }
                        if (sr2.EndOfStream)
                        {
                            read_message2 = false;
                            end2 = true;
                        }
                        if (read_message1)
                        {
                            message1 = sr.ReadLine();
                            message1 = sr.ReadLine();
                            if (message1 == null || message1 == "")
                            {
                                Console.WriteLine("null/empty1 aware");
                                data1 = null;
                            }
                            else
                            {
                                data1 = this.isolateInfoFromMessages(message1);
                                //Console.WriteLine(data1.Item1);
                                tof1 = this.makeTimeOfFlight(1, data1.Item1);
                                distance1 = this.calcDistFromTOF(tof1);
                            }
                        }
                        if (read_message2)
                        {
                            message2 = sr2.ReadLine();
                            message2 = sr2.ReadLine();
                            if (message2 == null || message2 == "")
                            {
                                Console.WriteLine("empty/null2 aware");
                                data2 = null;
                            }
                            else
                            {
                                
                                data2 = this.isolateInfoFromMessages(message2);
                                //Console.WriteLine(data2.Item1);
                                tof2 = this.makeTimeOfFlight(2, data2.Item1);
                                distance2 = this.calcDistFromTOF(tof2);

                            }
                        }
                        if ((Math.Abs((this.getDateTimeFromMessage(message1).Subtract(startTimeFromSimulator)).Seconds) <= this.allowableTimeLapse)
                            && (Math.Abs((this.getDateTimeFromMessage(message2).Subtract(startTimeFromSimulator)).Seconds) <= this.allowableTimeLapse))
                        {
                            read_message1 = false;
                            read_message2 = false;
                            outputToSimulator.Add(Tuple.Create(distance1, data1.Item1, data1.Item2, data1.Item3));
                            outputToSimulator.Add(Tuple.Create(distance2, data2.Item1, data2.Item2, data2.Item3));
                            //Console.WriteLine("here0");
                        }
                        else if ((Math.Abs((this.getDateTimeFromMessage(message1).Subtract(startTimeFromSimulator)).Seconds) <= this.allowableTimeLapse)
                        && ((this.getDateTimeFromMessage(message2).Subtract(startTimeFromSimulator)).Seconds) > this.allowableTimeLapse)
                        {
                            read_message1 = false;
                            read_message2 = false;
                            outputToSimulator.Add(Tuple.Create(distance1, data1.Item1, data1.Item2, data1.Item3));
                            //Console.WriteLine("here1");
                        } else if ((Math.Abs((this.getDateTimeFromMessage(message1).Subtract(startTimeFromSimulator)).Seconds) <= this.allowableTimeLapse)
                        && end2)
                        {
                            read_message1 = false;
                            read_message2 = false;
                            outputToSimulator.Add(Tuple.Create(distance1, data1.Item1, data1.Item2, data1.Item3));
                            //Console.WriteLine("here2");

                        }
                        else if ((Math.Abs((this.getDateTimeFromMessage(message2).Subtract(startTimeFromSimulator)).Seconds) <= this.allowableTimeLapse)
                        && ((this.getDateTimeFromMessage(message1).Subtract(startTimeFromSimulator)).Seconds) > this.allowableTimeLapse)
                        {
                            read_message1 = false;
                            read_message2 = false;
                            outputToSimulator.Add(Tuple.Create(distance2, data2.Item1, data2.Item2, data2.Item3));
                            //Console.WriteLine("here3");
                        }
                        else if ((Math.Abs((this.getDateTimeFromMessage(message2).Subtract(startTimeFromSimulator)).Seconds) <= this.allowableTimeLapse)
                        && end1)
                        {
                            read_message1 = false;
                            read_message2 = false;
                            outputToSimulator.Add(Tuple.Create(distance2, data2.Item1, data2.Item2, data2.Item3));
                            //Console.WriteLine("here3.5");

                        }
                        else if ((this.getDateTimeFromMessage(message1) < startTimeFromSimulator) &&
                            (this.getDateTimeFromMessage(message2) < startTimeFromSimulator))
                        {
                            read_message1 = true;
                            read_message2 = true;
                            //Console.WriteLine("here4");
                        }
                        else if (this.getDateTimeFromMessage(message1) < startTimeFromSimulator && !end1)
                        {
                            read_message1 = true;
                            read_message2 = false;
                            //Console.WriteLine("here5");
                        }
                        else if (this.getDateTimeFromMessage(message2) < startTimeFromSimulator && !end2)
                        {
                            read_message1 = false;
                            read_message2 = true;
                            //Console.WriteLine("here6");
                        }
                        else
                        {
                            read_message1 = false;
                            read_message2 = false;
                            //Console.WriteLine("here7");
                        }
                    }
                    return outputToSimulator;
                }
            }
        }

        public DateTime getInitialTime()
        {

            using (StreamReader sr = new StreamReader(@"../../../" + filename1 + ".csv"))
            {
                using (StreamReader sr2 = new StreamReader(@"../../../" + filename2 + ".csv"))
                {
                    string headerLine = sr.ReadLine();
                    string headerLine2 = sr2.ReadLine();
                    string message1 = "";
                    string message2 = "";

                    while (!sr.EndOfStream && !sr2.EndOfStream)
                    {
                        message1 = sr.ReadLine();
                        message1 = sr.ReadLine();

                        message2 = sr2.ReadLine();
                        message2 = sr2.ReadLine();


                        this.firstDateTimeVal1 = this.getDateTimeFromMessage(message1);
                        this.firstDateTimeVal2 = this.getDateTimeFromMessage(message2);

                        if (this.firstDateTimeVal1 < this.firstDateTimeVal2)
                        {
                            return this.firstDateTimeVal1;
                        }
                        return this.firstDateTimeVal2;
                    }
                    return new DateTime();
                }
            }
        }

        public DateTime getFinalTime()
        {
            using (StreamReader sr = new StreamReader(@"../../../" + filename1 + ".csv"))
            {
                using (StreamReader sr2 = new StreamReader(@"../../../" + filename2 + ".csv"))
                {
                    string lastline1 = string.Empty;
                    string lastline2 = string.Empty;
                    string line;
                    string headerLine = sr.ReadLine();
                    string headerLine2 = sr2.ReadLine();

                    while ((line = sr.ReadLine()) != null || line == "") {
                        lastline1 = line;
                    }
                    while ((line = sr2.ReadLine()) != null || line == "") {
                        lastline2 = line;
                    }

                    DateTime d1 = this.getDateTimeFromMessage(lastline1);
                    DateTime d2 = this.getDateTimeFromMessage(lastline2);

                    if (d1 > d2)
                    {
                        return d1;
                    }
                    return d2;
                }
            }
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
                        Tuple<DateTime, int, int> data = this.isolateInfoFromMessages(message);
                        // retrieve first datetime (this only happens once per run!!)
                        if (this.firstLiveDateTime)
                        {
                            this.firstLiveDateTimeVal = data.Item1;
                            this.firstLiveDateTime = false;
                        }
                        double tof = this.makeTimeOfFlight(0, data.Item1);
                        double distance = this.calcDistFromTOF(tof);

                        outputToPF = Tuple.Create(distance, data.Item1, data.Item2, data.Item3);
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

        public double makeTimeOfFlight(int sensor, DateTime dateTimeCurrent)
        {   /* 
             * param: sensor 0, 1, or 2
             * 0 means live serial date,
             * 1 means csv sensor 1
             * 2 means csv sensor2
             * returns: timeOfFlight
             */
            double tof;
            if (sensor == 0) // 0 means live serial data,
            {
                double diff1 = dateTimeCurrent.Subtract(this.firstLiveDateTimeVal).TotalSeconds;
                tof = diff1 % 8.179;
            }
            else if (sensor == 1)
            {
                double diff1 = dateTimeCurrent.Subtract(this.firstDateTimeVal1).TotalSeconds;
                tof = diff1 % 8.179;
            }
            else
            {
                double diff2 = dateTimeCurrent.Subtract(this.firstDateTimeVal2).TotalSeconds;
                tof = diff2 % 8.179;;
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

        public Tuple<DateTime, int, int> isolateInfoFromMessages(string message)
        {   /* 
             * Using raw serial data, we isolate dateTimes and transmitterIDs
             * 
             * returns: dateTime, transmitterID, and sensor id
             */
            string[] tempArr = message.Split(',');

            DateTime dateTimes = DateTime.Parse(tempArr[2]); //DateTimeOffset.Parse(tempArr[2]).UtcDateTime;
            string transmitterID = tempArr[4];
            string sensorID = tempArr[0];
            return Tuple.Create(dateTimes, Convert.ToInt32(transmitterID), Convert.ToInt32(sensorID));
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
    
// Useful GeoCoord:
//Tuple<double, double> tagCoord =
//    new Tuple<double, double>(33.57676, -43.52746);
//Tuple<double, double> sensorCoord =
//    new Tuple<double, double>(0, 0);

// get Distance w/ C# equivalent to python's geopy
//var myLocation = new GeoCoordinate(-51.39792, -0.12084);
//var yourLocation = new GeoCoordinate(-29.83245, 31.04034);
//double distance = myLocation.GetDistanceTo(yourLocation);

// Deviate from default serialport settings?
// More info
// @ https://docs.microsoft.com/en-us/dotnet/api/system.io.ports.serialport?view=dotnet-plat-ext-5.0
//SerialPort _serialPort = new SerialPort();
// Allow the user to set the appropriate properties.
//_serialPort.PortName = SetPortName(_serialPort.PortName);
//_serialPort.BaudRate = SetPortBaudRate(_serialPort.BaudRate);
//_serialPort.Parity = SetPortParity(_serialPort.Parity);
//_serialPort.DataBits = SetPortDataBits(_serialPort.DataBits);
//_serialPort.StopBits = SetPortStopBits(_serialPort.StopBits);
//_serialPort.Handshake = SetPortHandshake(_serialPort.Handshake);