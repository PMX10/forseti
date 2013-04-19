using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Foresti;
using LCM.LCM;

namespace LCMTestNode2
{
    class LCMTestNode2Display
    {
        public static void Main(string[] args)
        {
            LCM.LCM.LCM myLCM;

            try
            {
                myLCM = new LCM.LCM.LCM("udpm://239.255.76.67:7667?ttl=1");
                myLCM.SubscribeAll(new SimpleSubscriber());

                while (true)
                    System.Threading.Thread.Sleep(1000);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Ex: " + ex);
                Environment.Exit(1);
            }
        }

        internal class SimpleSubscriber : LCM.LCM.LCMSubscriber
        {
            public void MessageReceived(LCM.LCM.LCM lcm, string channel, LCM.LCM.LCMDataInputStream dins)
            {
                Console.WriteLine("RECV: " + channel);

                if (channel == "TestNode/Health")
                {
					Health_t msg = new Health_t(dins);

                    Console.WriteLine ("name=" + msg.name);
					Console.WriteLine ("uptime=" + msg.uptime);
                }
            }
        }
    }
}
