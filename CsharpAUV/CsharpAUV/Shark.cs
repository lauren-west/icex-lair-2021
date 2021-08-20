using System;
using System.Collections.Generic;
namespace CsharpAUV
{
    public class Shark
    {
        Random random_num = new Random();
        // SETS TYPE OF MEMBER VARIABLE
        public int SHARKNUMBER;
        public double X;
        public double Y;
        public double Z;
        public double THETA;
        public double V;
        public List<double> shark_list_x;
        public List<double> shark_list_y;
        public int INITIAL_PARTICLE_RANGE;

        public Shark()
        {
            this.INITIAL_PARTICLE_RANGE = 150;
            this.X = MyGlobals.random_num.Next(-INITIAL_PARTICLE_RANGE, INITIAL_PARTICLE_RANGE);
            this.Y = MyGlobals.random_num.Next(-INITIAL_PARTICLE_RANGE, INITIAL_PARTICLE_RANGE);
            this.Z = MyGlobals.random_num.Next(-INITIAL_PARTICLE_RANGE, INITIAL_PARTICLE_RANGE);
            this.V = MyGlobals.random_num.Next(0, 5);
            this.THETA = MyGlobals.random_num.NextDouble() * (2 * Math.PI) + -Math.PI;
            this.shark_list_x = new List<double>();
            this.shark_list_y = new List<double>();

        }
        static public double angle_wrap(double ang)
        {
            if (-Math.PI <= ang & ang <= Math.PI)
            {
                return ang;
            }
            else if (ang > Math.PI)
            {
                ang -= 2 * Math.PI;
                return angle_wrap(ang);
            }
            else
            {
                ang += 2 * Math.PI;
                return angle_wrap(ang);
            }
        }
        static public double velocity_wrap(double vel)
        {
            if (vel <= 2)
            {
                return vel;
            }
            else
            {
                vel += -2;
                return velocity_wrap(vel);
            }
        }
        public void create_shark_list()
        {
            this.shark_list_x = new List<double>();
            this.shark_list_y = new List<double>();

            this.shark_list_x.Add(this.X);
            this.shark_list_y.Add(this.Y);
        }

        public void update_shark()
        {
            // should update the sharks position after 
            double RANDOM_VELOCITY = 2;
            double RANDOM_THETA = Math.PI / 2;

            // updates velocity of particles
            this.V += MyGlobals.random_num.NextDouble() * RANDOM_VELOCITY;
            this.V = velocity_wrap(this.V);

            //change theta & pass through angle_wrap
            this.THETA += MyGlobals.random_num.NextDouble() * (2 * RANDOM_THETA) - RANDOM_THETA;
            this.THETA = angle_wrap(this.THETA);

            // change x & y coordinates to match
            this.X += this.V * Math.Cos(this.THETA);
            this.Y += this.V * Math.Sin(this.THETA);

        }

        public double calc_range_error(Robot currentRobot)
        {
            // calculates the average auv's position to the true sharks' position
            // adds gaussian noise to calculated_range_error

            double auvRange = Math.Sqrt(Math.Pow((this.Y - currentRobot.Y), 2) + Math.Pow((this.X - currentRobot.X), 2)) + MyGlobals.random_noise();
            return auvRange;
        }
        public double calc_range_error_real(Robot currentRobot)
        {
            // calculates the average auv's position to the true sharks' position

            double auvRange = Math.Sqrt(Math.Pow((this.Y - currentRobot.Y), 2) + Math.Pow((this.X - currentRobot.X), 2));
            return auvRange;
        }
    }
}

