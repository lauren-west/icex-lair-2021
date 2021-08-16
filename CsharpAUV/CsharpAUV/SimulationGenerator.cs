using System;
using System.Collections.Generic;
namespace CsharpAUV
{
    public class Simulation
    {
        public double rangeError;
        public int currentShark;
        public int currentRobot;
        public Simulation(double rangeError, int SharkNumber, int RobotNumber)
        {
            this.currentRobot = RobotNumber;
            this.currentShark = SharkNumber;
            this.rangeError = rangeError;

        }
        public void update_real_range_list()
        {
            MyGlobals.real_range_list[this.currentShark][this.currentRobot] = rangeError;
        }
    }
}
