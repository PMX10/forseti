using System;
using System.IO;
using System.Threading;
using System.Collections.Generic;

namespace Forseti
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Hello World!");

			Dictionary<int, string> filenames = new Dictionary<int, string>();
			
			filenames[1] = "working.cfg";
			filenames[2] = "working.cfg";
			filenames[3] = "working.cfg";
			filenames[4] = "working.cfg";

			for(int i = 1; i<=4; i++)
			{
//				string config = File.ReadAllText("" + i + ".cfg");
				string config = File.ReadAllText(filenames[i]);
				
				PiEMOSConfiger configer = new PiEMOSConfiger("10.20.34.10" + i, 6000 + i, 6000 + i, config);
				
				configer.Start();
//				while(true)
//				{
//					Console.WriteLine ("Sending");
//					configer.SendConfigData(config);
//					Thread.Sleep (500);
//				}
			}

			//configer.Start ();
		}
	}
}
