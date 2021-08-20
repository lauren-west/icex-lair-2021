using System;
using System.Collections.Generic;
using System.Linq;

namespace CsharpAUV
{
    public class ParticleFilter
    {
        public int NUMBER_OF_PARTICLES;
        public double Current_Time;
        public List<Particle> particleList = new List<Particle>();
        
        public double NUMBER_OF_AUVS;
        public List<double> w1_list_x;
        public List<double> w1_list_y;

        public List<double> w2_list_x;
        public List<double> w2_list_y;

        public List<double> w3_list_x;
        public List<double> w3_list_y;

        public List<double> errorList;

        public int sharkNumber;
        public int robotNumber;


        public ParticleFilter()
        {
            this.Current_Time = 0;
            this.NUMBER_OF_PARTICLES = 1000;
            
            this.w1_list_x = new List<double>();
            this.w2_list_x = new List<double>();
            this.w3_list_x = new List<double>();
            this.w1_list_y = new List<double>();
            this.w2_list_y = new List<double>();
            this.w3_list_y = new List<double>();
            this.errorList = new List<double>();
        }



        public void create()
        {

            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                particleList.Add(new Particle());
            }
            /* 
             Particle particle1 = new Particle();
             particle1.X = 45;
             particle1.Y = 45;
             particleList.Add(particle1);
             Particle particle2 = new Particle();
             particle2.X = 0;
             particle2.Y = 0;
             particleList.Add(particle2);
             Particle particle3 = new Particle();
             particle3.Y = -100;
             particle3.X = -100;
             particleList.Add(particle3);
             */

        }
        public void update()
        {
            // updates particles while simulated
            // returns new list of updated particles

            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                particleList[i].updateParticles();
            }

        }
        public void update_weights(List<List<double>> real_range_list, int SharkNumber)
        {
            // normalize new weights for each new shark measurement

            //[1,2], [20000,5]]

            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                double current_weight = 1;
                int robot_number = 0;
                foreach(double rangeError in real_range_list[SharkNumber] )
                {
                    if (rangeError != 20000)
                    {
                        double particle_range = particleList[i].calc_particle_range(MyGlobals.robot_list[robot_number]);
                        current_weight *= particleList[i].weight(real_range_list[SharkNumber][robot_number], particle_range);
                    }
                    robot_number += 1;
                }
                particleList[i].W = current_weight;
            }

        }
        public void correct()
        {
            //corrects the particles, adding more copies of particles based on how high the weight is
            List<Particle> tempList = new List<Particle>();

            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                if (particleList[i].W <= 0.333)
                {
                    Particle particle1 = particleList[i].DeepCopy();
                    tempList.Add(particle1);


                }
                else if (particleList[i].W <= 0.666)
                {
                    Particle particle1 = particleList[i].DeepCopy();
                    tempList.Add(particle1);
                    Particle particle2 = particleList[i].DeepCopy();
                    tempList.Add(particle2);

                }
                else
                {
                    Particle particle1 = particleList[i].DeepCopy();
                    tempList.Add(particle1);
                    Particle particle2 = particleList[i].DeepCopy();
                    tempList.Add(particle2);
                    Particle particle3 = particleList[i].DeepCopy();
                    tempList.Add(particle3);
                    Particle particle4 = particleList[i].DeepCopy();
                    tempList.Add(particle4);
                }

            }
            particleList = new List<Particle>();
            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                int index = MyGlobals.random_num.Next(0, tempList.Count);
                Particle particleIndex = tempList[index].DeepCopy();
                particleList.Add(particleIndex);

            }
        }

        public void weight_list_x()
        {
            w1_list_x = new List<double>();
            w2_list_x = new List<double>();
            w3_list_x = new List<double>();
            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                if (particleList[i].W <= 0.333)
                {
                    w1_list_x.Add(particleList[i].X);
                }
                else if (particleList[i].W <= 0.666)
                {
                    w2_list_x.Add(particleList[i].X);
                }
                else
                {
                    w3_list_x.Add(particleList[i].X);
                }

            }

        }
        public void weight_list_y()
        {
            w1_list_y = new List<double>();
            w2_list_y = new List<double>();
            w3_list_y = new List<double>();
            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                if (particleList[i].W <= 0.333)
                {
                    w1_list_y.Add(particleList[i].Y);
                }
                else if (particleList[i].W <= 0.666)
                {
                    w2_list_y.Add(particleList[i].Y);
                }
                else
                {
                    w3_list_y.Add(particleList[i].Y);
                }
            }
        }
        public List<double> predicting_shark_location()
        {
            double particle_total_x = 0;
            double particle_total_y = 0;
            for (int i = 0; i < NUMBER_OF_PARTICLES; ++i)
            {
                particle_total_x += particleList[i].X;
                particle_total_y += particleList[i].Y;
            }
            double particle_mean_x = particle_total_x / NUMBER_OF_PARTICLES;
            double particle_mean_y = particle_total_y / NUMBER_OF_PARTICLES;
            List<double> mean_particle = new List<double>();
            mean_particle.Add(particle_mean_x);
            mean_particle.Add(particle_mean_y);
            return mean_particle;
        }
    }


}