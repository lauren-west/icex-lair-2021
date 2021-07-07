// Lauren West, 07/07/2021 
// Contact Me: lwest@hmc.edu
using System;
using System.IO.Ports;

namespace CsharpSerialToAUV
{
    class SerialDataHandler
    {
        // member variables
        double time = 30; // seconds
        Tuple<double, double> tagCoordinates = new Tuple<double, double>(33.57676,-43.52746);
        Tuple<double, double> sensorCoordinates = new Tuple<double, double>(0.0, 0.0);

        // constructor
        SerialDataHandler(){
            // guess we are writing this later
        }

        public void getSerialData(){
            /*
            get_serial_data opens com port on PC in vs code
            returns: None
            */
        }


        static void Main(string[] args)
        {
            Console.WriteLine("Hello AUV!");
            SerialDataHandler handler = new SerialDataHandler();


        }
    }
}
