using System;
using System.IO;
using System.Threading;
using System.Collections;
using System.Collections.Generic;

namespace Forseti
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("PiEMOS-Configer starting...");

			Dictionary<int, string> filenames = new Dictionary<int, string>();

			filenames[1] = "working.cfg";
			filenames[2] = "working.cfg";
			filenames[3] = "working.cfg";
			filenames[4] = "working.cfg";

			Dictionary<int, bool> blues = new Dictionary<int, bool>();
			blues[1] = true;
			blues[2] = true;
			blues[3] = false;
			blues[4] = false;

			Dictionary<int, string> names = new Dictionary<int, string>();
			names[1] = "Impact";
			names[2] = "Ell Cerito";
			names[3] = "Lighthouse";
			names[4] = "Oakland Tech";

			Dictionary<int, int> numbers = new Dictionary<int, int>();
			numbers[1] = 15;
			numbers[2] = 28;
			numbers[3] = 30;
			numbers[4] = 29;
			//blues[1]


			for(int i = 1; i<=4; i++)
			{
//				string config = File.ReadAllText("" + i + ".cfg");
				string config = File.ReadAllText(filenames[i]);
				//Console.WriteLine ("config=" + config);

				PiEMOSConfiger configer = new PiEMOSConfiger("10.20.34.10" + i, 6000 + i, 6000 + i, config);

				configer.ConfigIsBlueAlliance = blues[i];
				configer.ConfigTeamName = names[i];
				configer.ConfigTeamNumber = numbers[i];


				configer.Start();

				configer.Start ();
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
