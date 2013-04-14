using System;

namespace Forseti
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("PiEMOSTimer starting...");
			for(int i = 1; i<=4; i++)
			{
				PiEMOSTimer timer = new PiEMOSTimer("10.20.34.10" + i, 6000 + i, 6000 + i);
				timer.Start();
				//				string config = File.ReadAllText("" + i + ".cfg");
//				string config = File.ReadAllText(filenames[i]);
				
//				PiEMOStimer timer = new PiEMOStimer("10.20.34.10" + i, 6000 + i, 6000 + i);
//				timer.Start();
				//				while(true)
				//				{
				//					Console.WriteLine ("Sending");
				//					configer.SendConfigData(config);
				//					Thread.Sleep (500);
				//				}
			}
		}
	}
}
