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
                List<Tuple<double, DateTime, int, int, double, double>> measurements = handler.getMeasurements1(currentTime);
                Console.WriteLine("current time: {0}",
                           currentTime.ToString("MM/dd/yyyy hh:mm:ss.fff tt"));
                if (measurements != null)
                {
                    // hand over to particle filter
                    foreach (Tuple<double, DateTime, int, int, double, double> item in measurements)
                    {

                        //Console.WriteLine(item.Item1);
                        Console.WriteLine("grabbed time: {0}",
                               item.Item2.ToString("MM/dd/yyyy hh:mm:ss.fff tt"));
                        //Console.WriteLine(item.Item3);
                        //Console.WriteLine(item.Item4);
                        //Console.WriteLine(item.Item5);
                        //Console.WriteLine(item.Item6);
                    }
                    Console.WriteLine();
                }
                else {
                     Console.WriteLine("measurements null");
                }
               

                // if new measurement
                // hand measurement over
                // else
                // not measurement
                // best way to do this?
                //create a member variable in handler named
                // previousPingDT
                // if dt in measurements is the same as the previousPingDT
                //  this is NOT new data, do not give to particle filter
                // else:
                //  new data, hand it over!




                //Console.WriteLine();



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

