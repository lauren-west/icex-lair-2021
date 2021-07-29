using System;
using System.Collections.Generic;
namespace CsharpAUV
{
    public class Simulator
    {
        public Simulator()
        {
        }
        static void Main(string[] args)
        {
            SerialDataHandler handler = new SerialDataHandler("sensor1", "sensor2");
            DateTime currentTime = handler.getInitialTime();
            DateTime finalTime = handler.getFinalTime();

            while (currentTime < finalTime)
            {
                List<Tuple<double, DateTime, string, string>> measurements = handler.getMeasurements(currentTime);

                // run pf to estimate shark state

                // plan based on shark state

                // control

                currentTime = currentTime.AddSeconds(1);
            }
            Console.WriteLine("Done");
        }
    }
}
