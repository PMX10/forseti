using System;
using System.Collections.Generic;
using System.Threading;
using Pololu.Usc;
using Pololu.UsbWrapper;


namespace Forseti
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Starting Maestro driver...");
			List<DeviceListItem> connectedDevices = Usc.getConnectedDevices();
			Console.WriteLine ("Number of MicroMaestros detected=" + connectedDevices.Count);


            GoalFlags[] goals = new GoalFlags[4];
			Dictionary<string, int> goalIDs = new Dictionary<string, int>();
			goalIDs.Add("00032615", 3);//D
			goalIDs.Add("00031531", 2);//C
			goalIDs.Add("00032614", 1);//B			
            goalIDs.Add("00032598", 0);//A

			foreach (DeviceListItem dli in connectedDevices)
			{
				Console.WriteLine (
					"Detected Maestro: {serialNumber=" + dli.serialNumber + 
					", text=" + dli.text + "}");
				goals[goalIDs[dli.serialNumber]] = new GoalFlags(new Usc(dli));
			}

            CubeRouteField field = new CubeRouteField(goals);

            foreach (GoalFlags flags in goals)
            {
                for(int i = 0; i< 5; i++)
                {
                    flags.setFlagPosition(i, 0);
                }
            }
                    

            GoalLightsConnection conn = new GoalLightsConnection(field, "10.20.34.100", 9000, 9000);
//            GoalLightsConnection conn = new GoalLightsConnection(null, "127.0.0.1", 9001, 9000);
            Console.WriteLine ("Running...");
            conn.Run ();
		}
	}
}
