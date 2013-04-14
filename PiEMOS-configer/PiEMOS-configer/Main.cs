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

			int match = 1;

//			Dictionary<Team, string> configs = new Dictionary<Team, string> ();

			List<Team> teams = ITQueries.GetMatch (match);

//			foreach (Team t in teams) {
//				configs [t] = ITQueries.GetTeamConfig (t.number);
//			}

			for (int i = 1; i<=4; i++) {
				string config = ITQueries.GetTeamConfig (i);
				Hashtable teamInfo = new Hashtable ();
				teamInfo.Add ("IsBlueAlliace", i <= 2);
				teamInfo.Add ("TeamNumber", teams [i].number);
				teamInfo.Add ("TeamName", teams [i].name);

				
				PiEMOSConfiger configer = new PiEMOSConfiger ("10.20.34.10" + i, 6000 + i, 6000 + i, config);

				configer.TeamInfo = teamInfo;

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
