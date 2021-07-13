using System;
using System.IO.Ports;
using System.Threading;
using System.Device.Location;
using System.Collections.Generic;
using System.Globalization;
using System.Collections;


namespace CsharpAUV
{
    class SerialDataHandler
    {
        static bool _continue;
        static SerialPort _serialPort;

        int timeToRun = 30; // seconds
        Tuple<double, double> tagGpsCoord =
            new Tuple<double, double>(33.57676, -43.52746);
        Tuple<double, double> sensorGpsCoord =
            new Tuple<double, double>(0, 0);
        public List<string> outputList;
        static double temp = 12; // (Celsius)
        static double depth = 10; // (meters)
        static double salinity = 33.5; // (ppt) Default: 33.5
        // the mackenzie equation for speed of sound underwater
        // http://resource.npl.co.uk/acoustics/techguides/soundseawater/content.html
        double speedOfSound = 1448.96 + (4.591 * temp) -
            (5.304 * Math.Pow(10,-2) * Math.Pow(temp,2)) +
            (2.374 * Math.Pow(10,-4) * Math.Pow(temp,3)) +
            (1.340 * (salinity-35)) + (1.630 * Math.Pow(10,-2) * depth) +
            (1.675 * Math.Pow(10,-7)* Math.Pow(depth,2)) -
            (1.025 * Math.Pow(10,-2)* temp * (salinity-35)) -
            (7.139 * Math.Pow(10,-13)* temp * Math.Pow(depth,3));

        // constructor
        public SerialDataHandler()
        {
            this.outputList = new List<string>();
        }
        static void Main(string[] args)
        {
            Console.WriteLine("Hi Joan Caitlyn Hannah Roman!");

            string name;
            string message;
            StringComparer stringComparer = StringComparer.OrdinalIgnoreCase;
            Thread readThread = new Thread(Read);
            SerialDataHandler serialdatahandler = new SerialDataHandler();

            // Create a new SerialPort object with default settings.

            SerialPort _serialPort = new SerialPort("COM3", 9600);

            // Allow the user to set the appropriate properties.
            _serialPort.PortName = SetPortName(_serialPort.PortName);
            _serialPort.BaudRate = SetPortBaudRate(_serialPort.BaudRate);
            _serialPort.Parity = SetPortParity(_serialPort.Parity);
            _serialPort.DataBits = SetPortDataBits(_serialPort.DataBits);
            _serialPort.StopBits = SetPortStopBits(_serialPort.StopBits);
            _serialPort.Handshake = SetPortHandshake(_serialPort.Handshake);

            // get Distance w/ C# equivalent to python's geopy
            //var myLocation = new GeoCoordinate(-51.39792, -0.12084);
            //var yourLocation = new GeoCoordinate(-29.83245, 31.04034);
            //double distance = myLocation.GetDistanceTo(yourLocation);


            //Set the read / write timeouts
            _serialPort.ReadTimeout = 500;
            _serialPort.WriteTimeout = 500;

            _serialPort.Open();
            _continue = true;
            readThread.Start();
            

            Console.Write("Name: ");
            name = Console.ReadLine();

            Console.WriteLine("Type QUIT to exit");

            while (_continue)
            {
                message = Console.ReadLine();
                serialdatahandler.outputList.Add(message);

                if (stringComparer.Equals("quit", message))
                {
                    _continue = false;
                }
                else
                {
                    _serialPort.WriteLine(
                        String.Format("<{0}>: {1}", name, message));
                }
            }

            readThread.Join();
            _serialPort.Close();

            // start using data
            Tuple<List<DateTime>, List<string>> data = serialdatahandler.makeData();
            // retrieve totalTimes Lsit and timeOfFlight List
            var (totalTime, timeOfFlight) = serialdatahandler.makeTimeOfFlightList(data.Item1);

            List<double> distances = new List<double>();
            for (int i = 0; i < timeOfFlight.Count; i++) {
                distances.Add(serialdatahandler.speedOfSound * timeOfFlight[i]);
            }

        }

        public double getDistFromTOF(List<DateTime> dateTimes)
        {
            // getting predicted distance from TOF

            return 0.0;
        }

            public Tuple<List<double>, List<double>> makeTimeOfFlightList(List<DateTime> dateTimes) {
            List<double> totalTime = new List<double>();
            List<double> timeOfFlight = new List<double>();
            DateTime initialTime = dateTimes[0];
            for (int i = 1; i < dateTimes.Count; i++) {
                double diff1 = dateTimes[i].Subtract(initialTime).TotalSeconds;
                totalTime.Add(diff1);
                timeOfFlight.Add(diff1 % 8.179); // add total time % 8.179 to get tof
            }
            return Tuple.Create(totalTime, timeOfFlight);
        }

        public Tuple<List<DateTime>, List<string>> makeData()
        {
            //string dateString = "yyyy-MM-dd HH:mm:ss.fff";
            List<DateTime> dateTimes = new List<DateTime>();
            List<string> transmitterID = new List<string>();

            // split up the outputList
            foreach (string line in outputList) {
                string[] tempArr = line.Split();
                if (tempArr.Length <= 10)
                {
                    transmitterID.Add(tempArr[4]);
                    dateTimes.Add(DateTimeOffset.Parse(tempArr[2]).UtcDateTime);
                    // TRY # 2 if above line doesn't work as desired.
                    //dateTimes[line] = DateTime.ParseExact(tempArray[2], dateString, CultureInfo.InvariantCulture);
                }
            }
            ArrayList DataList = new ArrayList();
            DataList.Add(dateTimes);
            DataList.Add(transmitterID);

            return Tuple.Create(dateTimes, transmitterID);

        }

        public static void Read()
        {
            while (_continue)
            {
                try
                {
                    string message = _serialPort.ReadLine();
                    Console.WriteLine(message);
                }
                catch (TimeoutException) { }
            }
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
