using System;
using LCM;
using Foresti;

namespace LCMTestNode
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Hello World!");
            try
            {
                LCM.LCM.LCM myLCM = new LCM.LCM.LCM("udpm://239.255.76.67:7667?ttl=1");

                Health_t msg = new Health_t();
                TimeSpan span = DateTime.Now - new DateTime(1970, 1, 1);
                msg.uptime = span.Ticks * 100;
                msg.name = "LCMTestNode";
				myLCM.Publish ("TestNode/Health", msg);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Ex: " + ex);
            }
		}
	}
}
