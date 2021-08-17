using System;
using System.Collections.Generic;
namespace CsharpAUV
{
    public class Simulator
    {
        public int NUMBER_OF_SHARKS;
        public int NUMBER_OF_ROBOTS;
        public int NUMBER_OF_PARTICLEFILTERS;
        public List<List<ParticleFilter>> particleFilterList = new List<List<ParticleFilter>>();
        public List<List<Simulation>> simulationList = new List<List<Simulation>>();
        public List<List<double>> cartesianList = new List<List<double>>();
        public Dictionary<double, Dictionary<double, double>> sharkDict = new Dictionary<double, Dictionary<double, double>>();
        public void create_real_range_list()
        {
            for(int i = 0; i < NUMBER_OF_SHARKS; ++i)
            {
                List<double> newList = new List<double>();
                foreach (Robot r1 in MyGlobals.robot_list)
                {
                    newList.Add(20000);
                }
                MyGlobals.real_range_list.Add(newList);
            }
        }
        public void create_and_initialize_particle_filter()
        {
            for (int s = 0; s < NUMBER_OF_SHARKS; ++s)
            {
                List<ParticleFilter> partylist = new List<ParticleFilter>();
                for (int r = 0; r < NUMBER_OF_ROBOTS; ++r)
                {
                    ParticleFilter p1 = new ParticleFilter();
                    p1.create();
                    partylist.Add(p1);
                }
                this.particleFilterList.Add(partylist);
            }
        }
        public void create_and_initialize_robots()
        {
            foreach (int sensorNumber in MyGlobals.sensor_list)
            {
                int SENSOR_INDEX = MyGlobals.sensor_list.IndexOf(sensorNumber);
                Robot newRobot = new Robot(sensorNumber,cartesianList[SENSOR_INDEX][0], cartesianList[SENSOR_INDEX][1]);
                MyGlobals.robot_list.Add(newRobot);
                
            }
        }
        // calibration
        public void create_simulation()
        {
            for (int i = 0; i< NUMBER_OF_SHARKS; ++i)
            {
                List<Simulation> currentSharkSim = new List<Simulation>();
                for(int j = 0; j < NUMBER_OF_ROBOTS; ++j)
                {
                    double rangeError = 0;
                    Simulation sim = new Simulation(rangeError, i, j);
                    currentSharkSim.Add(sim);

                }
                simulationList.Add(currentSharkSim);
            }
        }
        public void create_and_update_sharks(double transmitterID, double sensorID, double predicted_distance)
        {
            bool inDict = sharkDict.ContainsKey(transmitterID);
            
            if (inDict)
            {
                bool inSensorDict = sharkDict[transmitterID].ContainsKey(sensorID);
                if (inSensorDict)
                {
                    sharkDict[transmitterID][sensorID] = predicted_distance;
                    
                }
                else
                {
                    sharkDict[transmitterID].Add(sensorID, predicted_distance);
                }
                
            }
            else
            {
                MyGlobals.shark_list.Add(transmitterID);
                Dictionary<double, double> currentDict = new Dictionary<double, double>();
                currentDict.Add(sensorID, predicted_distance);
                sharkDict.Add(transmitterID, currentDict);
            }
        }
        public void update_robots()
        {
            foreach (Robot r1 in MyGlobals.robot_list)
            {
                r1.update_robot_position();
            }
        }

        public void update_pfs()
        {
            int sharkNum = 0;
            foreach (List<ParticleFilter> pflist in particleFilterList)
            {
                foreach (ParticleFilter pf in pflist)
                {
                    pf.update();
                    pf.update_weights(MyGlobals.real_range_list, sharkNum);
                    pf.correct();

                }

                sharkNum += 1;
            }
        }
        public double CALC_RANGE_ERROR(List<double> meanP, List<double> SharkCoords)// msg
        {
            //calculates the range from the Shark to the Mean
            double particleRange = Math.Sqrt(Math.Pow((meanP[1] - SharkCoords[1]), 2) + Math.Pow((meanP[0] - SharkCoords[0]), 2));
            return particleRange;
        }
        public List<List<double>> mean_pfs(List<double> SharkCoords)
        {
            List<List<double>> rangeList = new List<List<double>>();
            foreach (List<ParticleFilter> pflist in particleFilterList)
            {
                int robotNum = 0;
                List<double> rangeList1 = new List<double>();
                foreach (ParticleFilter pf in pflist)
                {
                    List<double> meanP = pf.predicting_shark_location();
                    
                    rangeList1.Add(CALC_RANGE_ERROR(meanP, SharkCoords));
                    robotNum += 1;
                }
                rangeList.Add(rangeList1);
                
            }
            return rangeList;
        }
        public void clear_real_range_list()
        {
            List<List<double>> newList = new List<List<double>>();
            MyGlobals.real_range_list = newList;
            create_real_range_list();
        }

        public void update_real_range_list(double transmitterID, double sensorID)
        {
            int SharkNum = MyGlobals.shark_list.IndexOf(transmitterID);
            
            int RobotNum = MyGlobals.sensor_list.IndexOf(sensorID);
            
            MyGlobals.real_range_list[SharkNum][RobotNum] = sharkDict[transmitterID][sensorID];

        }
        public List<double> convertToCartesian(double lat2, double lon2)
        {
            List<double> cartesianList = new List<double>();
            double lat1 = 33.480467;
            double lon1 = -117.735645;
            double EarthRadius = 6271000;
            double phi1 = lat1 * Math.PI / 180;
            double phi2 = lat2 * Math.PI / 180;
            double delta_phi = (lat2 - lat1) * Math.PI / 180;
            double delta_lambda = (lon2 - lon1) * Math.PI / 180;

            double a = Math.Sin(delta_phi / 2) * Math.Sin(delta_phi / 2)
                    + Math.Cos(phi1) * Math.Cos(phi2)
                    * Math.Sin(delta_lambda / 2) * Math.Sin(delta_lambda / 2);

            double c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));

            double distance = EarthRadius * c;

            // converting to get Beta
            double dLong = lon2 - lon1;
            double x = Math.Cos(lat2) * Math.Sin(dLong);
            double y = (Math.Cos(lat1) * Math.Sin(lat2)) - (Math.Sin(lat1) * Math.Cos(lat2) * Math.Cos(dLong));

            // finding beta...
            double Beta_in_radians = Math.Atan2(x, y);

            double Beta = Beta_in_radians * (180 / Math.PI);


            // using beta to return Cartesian of robot

            double x_real = distance * Math.Cos(Beta);
            cartesianList.Add(x_real);
            double y_real = distance * Math.Sin(Beta);
            cartesianList.Add(y_real);
            return cartesianList;
        }
        
        public Simulator()
        {
          
        }
        
        static void Main(string[] args)
        {
            Simulator sim = new Simulator();
            SerialDataHandler handler = new SerialDataHandler("fake1", "fake2");

            sim.NUMBER_OF_SHARKS = 1;
            sim.NUMBER_OF_ROBOTS = 2;
            sim.NUMBER_OF_PARTICLEFILTERS = sim.NUMBER_OF_ROBOTS * sim.NUMBER_OF_SHARKS;

            int sensor1 = handler.getSensorSerialNum(1);
            MyGlobals.sensor_list.Add(sensor1);// list of all the sensors
            List<double> current1 = handler.getLatitude(1);

            MyGlobals.coordinate_list.Add(current1); // list of all the initial GPS coords

            int sensor2 = handler.getSensorSerialNum(2);
            MyGlobals.sensor_list.Add(sensor2);
            List<double> current = handler.getLatitude(2);
            MyGlobals.coordinate_list.Add(current);

            foreach (List<double> coordinateList in MyGlobals.coordinate_list)
            {
                List<double> currentCartesian = sim.convertToCartesian(coordinateList[0], coordinateList[1]);
                sim.cartesianList.Add(currentCartesian);
            }
            // sensor 1
            Console.WriteLine("Sensor Cartesian");
            Console.WriteLine(sim.cartesianList[0][0]);
            Console.WriteLine(sim.cartesianList[0][1]);

            Console.WriteLine("creating Shark coordinates");
            double SharkLat = 33.480447;
            double SharkLong = -117.734242;
            List<double> SharkCoords = sim.convertToCartesian(SharkLat, SharkLong);

            // updating sensor 2's cartesian coordinates
            

            sim.create_and_initialize_robots();
            sim.create_real_range_list();
            sim.create_and_initialize_particle_filter();

            DateTime currentTime = handler.getInitialTime();
            DateTime finalTime = handler.getFinalTime();
            
            while (currentTime < finalTime)
            {
                sim.update_robots();
                List<Tuple<double, DateTime, int, int, double, double>> measurements = handler.getMeasurements1(currentTime);
                Console.WriteLine("current time: {0}",
                           currentTime.ToString("MM/dd/yyyy hh:mm:ss.fff tt"));

                // keep track of information based on the shark
                //          sort based on which transmitterID --> assigns rangeError to them
                Console.WriteLine("Predicted Distance");

                if (measurements != null)
                {
                    // hand over to particle filter
                    foreach (Tuple<double, DateTime, int, int, double, double> item in measurements)
                    {
                        sim.create_and_update_sharks(item.Item3, item.Item4, item.Item1);
                        sim.update_real_range_list(item.Item3, item.Item4);
                        Console.WriteLine(item.Item1);
                        Console.WriteLine("grabbed time: {0}",
                        item.Item2.ToString("MM/dd/yyyy hh:mm:ss.fff tt"));
                        //ToDo: update the Shark's 
                    }
                    Console.WriteLine();
                }
                else
                {
                    Console.WriteLine("measurements null");
                }

                //// Step 2: Run pf to estimate shark state
                sim.update_pfs();
                //// Step 3: Plan based on shark state
                
                //// Step 4: Control
                sim.clear_real_range_list();
                List<List<double>> simList = sim.mean_pfs(SharkCoords);
                Console.WriteLine("range Error");
                Console.WriteLine(simList[0][0]);
                Console.WriteLine(simList[0][1]);

                currentTime = currentTime.AddSeconds(1);
            }
            
            Console.WriteLine();
            Console.WriteLine("Done");
 
        }
    }
}

