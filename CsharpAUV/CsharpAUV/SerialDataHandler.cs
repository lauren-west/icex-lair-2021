using System;
using System.IO;
using System.IO.Ports;
using System.Collections.Generic;
using System.Collections;
using System.Diagnostics;

namespace CsharpAUV
{
    class SerialDataHandler
    {
        static SerialPort _serialPort;
        //public List<string> rawSerialData = new List<string>();
        double speedOfSound;
        int timeToRun;
        DateTime firstDateTimeVal;
        DateTime firstDateTimeVal1;
        DateTime firstDateTimeVal2;

        // contains most recent measurement from serial port
        List<Tuple<double, DateTime, string, string>> outputToParticleFilter = new List<Tuple<double, DateTime, string, string>>();

        public SerialDataHandler()
        {
        }

        static void Main(string[] args)
        {
            // 457049,148,2021-07-22 11:16:09.666
            DateTime start_time_from_pf = new DateTime(2021, 7, 22, 4, 16, 9, 666);
            Console.WriteLine(start_time_from_pf);
            Console.WriteLine("Welcome.");
            SerialDataHandler serialdatahandler = new SerialDataHandler();
            string message;
            string message1 = "";
            string message2 = "";
            string line1;
            string line2;
            int allowableTimeLapse = 4;
            bool firstDatetime = true;
            bool firstDatetime1 = true;
            bool firstDatetime2 = true;

            if (serialdatahandler.runCSV())
            {
                // assume speed of sound for old data is a default 1500
                serialdatahandler.speedOfSound = 1500;
                Console.WriteLine("Input csv file name without file type");
                string filename1 = Console.ReadLine();
                Console.WriteLine("Input csv file name without file type");
                string filename2 = Console.ReadLine();

//457049,148,2021-07-22 11:16:09.666,A69-1602,65477,80.5,37.5,0,#A4,"(34.109135, -117.71281)","(34.109172, -117.71241)",122.686929,38,0.0008575714285647962,1.2520542857046024


                //(@"C:\" + filename + ".csv") old file path
                using (StreamReader sr = new StreamReader(@"../../../" + filename1 + ".csv"))
                {
                    using (StreamReader sr2 = new StreamReader(@"../../../" + filename2 + ".csv"))
                    {
                        string headerLine = sr.ReadLine();
                        string headerLine2 = sr2.ReadLine();
                        double tof1, tof2;
                        double distance1 = -1.0;
                        double distance2 = -1.0;
                        bool read_message1 = true;
                        bool read_message2 = true;

                        Tuple<DateTime, string, string> data1 = Tuple.Create(new DateTime(), "", "");
                        Tuple<DateTime, string, string> data2 = Tuple.Create(new DateTime(), "", "");

                        //while (!sr.EndOfStream && !sr2.EndOfStream) 
                        while (read_message1 || read_message2)
                        {
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
                                    data1 = serialdatahandler.isolateInfoFromMessages(message1);
                                    // retrieve first datetime (this only happens once per run!!)
                                    Console.WriteLine("Message 1:");
                                    Console.WriteLine(data1.Item1);

                                    if (firstDatetime1)
                                    {
                                        serialdatahandler.firstDateTimeVal1 = data1.Item1;
                                        firstDatetime1 = false;
                                    }

                                    tof1 = serialdatahandler.makeTimeOfFlight(1, data1.Item1);
                                    distance1 = serialdatahandler.calcDistFromTOF(tof1);
                                    Console.Write("TOF1: ");
                                    Console.WriteLine(tof1);
                                    Console.Write("Distance1: ");
                                    Console.WriteLine(distance1);
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
                                    if (firstDatetime2)
                                    {
                                        serialdatahandler.firstDateTimeVal2 = serialdatahandler.getDateTimeFromMessage(message2);
                                        firstDatetime2 = false;
                                    }
                                    data2 = serialdatahandler.isolateInfoFromMessages(message2);
                                    // retrieve first datetime (this only happens once per run!!)
                                    Console.WriteLine("Message 2:");
                                    Console.WriteLine(data2.Item1);
                                    tof2 = serialdatahandler.makeTimeOfFlight(2, data2.Item1);
                                    Console.Write("TOF2: ");
                                    Console.WriteLine(tof2);
                                    distance2 = serialdatahandler.calcDistFromTOF(tof2);
                                    Console.Write("Distance2: ");
                                    Console.WriteLine(distance2);
                                }
                            }
                            if ((Math.Abs((serialdatahandler.getDateTimeFromMessage(message1).Subtract(start_time_from_pf)).Seconds) <= allowableTimeLapse)
                                && (Math.Abs((serialdatahandler.getDateTimeFromMessage(message2).Subtract(start_time_from_pf)).Seconds) <= allowableTimeLapse))
                            {
                                read_message1 = false;
                                read_message2 = false;
                                serialdatahandler.outputToParticleFilter.Add(Tuple.Create(distance1, data1.Item1, data1.Item2, data1.Item3));
                                serialdatahandler.outputToParticleFilter.Add(Tuple.Create(distance2, data2.Item1, data2.Item2, data2.Item3));
                           
                                Console.WriteLine("return packet to PF (both message1 and 2)");
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[0].Item1);
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[1].Item1);
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[0].Item2);
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[1].Item2);
                            }
                            else if ((Math.Abs((serialdatahandler.getDateTimeFromMessage(message1).Subtract(start_time_from_pf)).Seconds) <= allowableTimeLapse)
                            && ((serialdatahandler.getDateTimeFromMessage(message2).Subtract(start_time_from_pf)).Seconds) > allowableTimeLapse)
                            {
                                read_message1 = false;
                                read_message2 = false;
                                serialdatahandler.outputToParticleFilter.Add(Tuple.Create(distance1, data1.Item1, data1.Item2, data1.Item3));
                                Console.WriteLine("return packet to PF, message1 only");
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[0].Item1);
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[0].Item2);
                            }
                            else if ((Math.Abs((serialdatahandler.getDateTimeFromMessage(message2).Subtract(start_time_from_pf)).Seconds) <= allowableTimeLapse)
                            && ((serialdatahandler.getDateTimeFromMessage(message1).Subtract(start_time_from_pf)).Seconds) > allowableTimeLapse)
                            {
                                read_message1 = false;
                                read_message2 = false;
                                serialdatahandler.outputToParticleFilter.Add(Tuple.Create(distance2, data2.Item1, data2.Item2, data2.Item3));
                                
                                Console.WriteLine("return packet to PF, just message 2)");
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[0].Item1);
                                Console.WriteLine(serialdatahandler.outputToParticleFilter[0].Item2);
                            }
                            else if ((serialdatahandler.getDateTimeFromMessage(message1) < start_time_from_pf) &&
                                (serialdatahandler.getDateTimeFromMessage(message2) < start_time_from_pf))
                            {
                                read_message1 = true;
                                read_message2 = true;
                                //Console.WriteLine("truetrue");
                            }
                            else if (serialdatahandler.getDateTimeFromMessage(message1) < start_time_from_pf)
                            {
                                read_message1 = true;
                                read_message2 = false;
                                //Console.WriteLine("truefalse");
                            }
                            else if (serialdatahandler.getDateTimeFromMessage(message2) < start_time_from_pf)
                            {
                                read_message1 = false;
                                read_message2 = true;
                                //Console.WriteLine("falsetrue");
                            }
                            else
                            {
                                read_message1 = false;
                                read_message2 = false;
                                //Console.WriteLine("falsefalse");
                            }
                        }
                    }
                }
            }
            else
            {
                StringComparer stringComparer = StringComparer.OrdinalIgnoreCase;
                serialdatahandler.speedOfSound = serialdatahandler.calcSpeedOfSound();
                serialdatahandler.timeToRun = serialdatahandler.getTimeToRun();

                // Create a new SerialPort object with default settings.
                _serialPort = new SerialPort();

                _serialPort.PortName = SetPortName(_serialPort.PortName);

                //Set the read / write timeouts
                _serialPort.ReadTimeout = 500;
                _serialPort.WriteTimeout = 500;

                Console.WriteLine("Beginning to listen to " + _serialPort.PortName + ".");

                _serialPort.Open();

                Stopwatch sw = new Stopwatch();
                sw.Start();

                while (sw.ElapsedMilliseconds < serialdatahandler.timeToRun)
                {
                    try
                    {
                        message = _serialPort.ReadLine();
                        //serialdatahandler.rawSerialData.Add(message);
                        if (message != null)
                        {
                            Tuple<DateTime, string, string> data = serialdatahandler.isolateInfoFromMessages(message);
                            // retrieve first datetime (this only happens once per run!!)
                            if (firstDatetime)
                            {
                                serialdatahandler.firstDateTimeVal = data.Item1;
                                firstDatetime = false;
                            }
                            double tof = serialdatahandler.makeTimeOfFlight(0, data.Item1);
                            double distance = serialdatahandler.calcDistFromTOF(tof);

                            //outputToParticleFilter = distance, datetime, transmitterID, sensorID
                            serialdatahandler.outputToParticleFilter.Add(Tuple.Create(distance, data.Item1, data.Item2, data.Item3));
                        }
                    }
                    catch (TimeoutException) { }
                }
                _serialPort.Close();
            }
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
            if (sensor == 0)
            {
                double diff1 = dateTimeCurrent.Subtract(this.firstDateTimeVal).TotalSeconds;
                tof = diff1 % 8.179; ; // add total time % 8.179 to get tof
            }
            else if (sensor == 1)
            {
                double diff1 = dateTimeCurrent.Subtract(this.firstDateTimeVal1).TotalSeconds;
                tof =  diff1 % 8.179; ; // add total time % 8.179 to get tof
            }
            else {
                double diff2 = dateTimeCurrent.Subtract(this.firstDateTimeVal2).TotalSeconds;
                tof =  diff2 % 8.179; ; // add total time % 8.179 to get tof}
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
            //Console.WriteLine(message);
            string[] tempArr = message.Split(',');

            return DateTime.Parse(tempArr[2]).ToLocalTime();
        }

        public Tuple<DateTime, string, string> isolateInfoFromMessages(string message)
        {   /* 
             * Using raw serial data, we isolate dateTimes and transmitterIDs
             * 
             * returns: dateTime, transmitterID, and sensor id
             */

            DateTime dateTimes = new DateTime();
            string transmitterID = "";
            string sensorID = "";

            //Console.WriteLine(message);
            string[] tempArr = message.Split(',');
            sensorID = tempArr[0];
            transmitterID = tempArr[4];
            dateTimes = DateTime.Parse(tempArr[2]).ToLocalTime(); //DateTimeOffset.Parse(tempArr[2]).UtcDateTime;

            return Tuple.Create(dateTimes, transmitterID, sensorID);
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


// Have not used:
//Tuple<double, double> tagCoord =
//    new Tuple<double, double>(33.57676, -43.52746);
//Tuple<double, double> sensorCoord =
//    new Tuple<double, double>(0, 0);

// get Distance w/ C# equivalent to python's geopy
//var myLocation = new GeoCoordinate(-51.39792, -0.12084);
//var yourLocation = new GeoCoordinate(-29.83245, 31.04034);
//double distance = myLocation.GetDistanceTo(yourLocation);

// deviate from default serialport settings
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
