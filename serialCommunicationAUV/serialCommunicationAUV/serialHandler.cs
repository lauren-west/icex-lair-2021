using System;
using System.IO;
using System.IO.Ports;


namespace serialCommunicationAUV
{
    public class serialHandler
    {

        static void Main(string[] args)
        {

            //int timeToRun = 30; // seconds
            //Tuple<double, double> tagGpsCoord =
            //    new Tuple<double, double>(33.57676, -43.52746);
            //Tuple<double, double> sensorGpsCoord =
            //    new Tuple<double, double>(0, 0);



            //// constructor
            //SerialDataHandler()
            //{
            //    // guess we are writing this later
            //}

            //public void getSerialData()
            //{
            //    /*
            //    get_serial_data opens com port on PC in vs code
            //    returns: None
            //    */
            //}

            Console.WriteLine("Hi Joan Caitlyn Hannah Roman!");
            //SerialDataHandler handler = new SerialDataHandler();
            SerialPort mySerialPort = new SerialPort("COM3", 9600);
            try
            {
                mySerialPort.Open();
                mySerialPort.Close();
            }
            catch (IOException ex)
            {
                Console.WriteLine(ex);
            }
        }
    }
}
        
