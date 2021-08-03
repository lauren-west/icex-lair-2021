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
            SerialDataHandler handler = new SerialDataHandler("fake1", "fake2");
            DateTime currentTime = handler.getInitialTime();
            DateTime finalTime = handler.getFinalTime();

            while (currentTime < finalTime)
            {
                // Step 1: Get Measurements
                List<Tuple<double, DateTime, int, int>> measurements = handler.getMeasurements(currentTime);
                foreach (Tuple<double, DateTime, int, int> item in measurements)
                {
                    Console.WriteLine(item.Item1);
                    Console.WriteLine(item.Item2);
                    Console.WriteLine(item.Item3);
                    Console.WriteLine(item.Item4);
                    Console.WriteLine();
                }

                // Step 2: Run pf to estimate shark state

                // Step 3: Plan based on shark state

                // Step 4: Control



                currentTime = currentTime.AddSeconds(1);
            }
            
            Console.WriteLine();
            Console.WriteLine("Done");
        }
    }
}

