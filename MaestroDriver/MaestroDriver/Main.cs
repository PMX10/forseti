using System;
using System.Collections.Generic;
using System.Threading;
using Pololu.Usc;
using Pololu.UsbWrapper;
using Foresti;
using LCM.LCM;

namespace Forseti
{
	class MainClass
	{
		public static void Main (string[] args)
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
//			Console.WriteLine ("Starting Maestro driver...");
//			List<DeviceListItem> connectedDevices = Usc.getConnectedDevices();
//			Console.WriteLine ("Number of MicroMaestros detected=" + connectedDevices.Count);
//
//
//            GoalFlags[] goals = new GoalFlags[4];
//			Dictionary<string, int> goalIDs = new Dictionary<string, int>();
//			goalIDs.Add("00032615", 3);//D
//			goalIDs.Add("00031531", 2);//C
//			goalIDs.Add("00032614", 1);//B			
//            goalIDs.Add("00032598", 0);//A
//
//			foreach (DeviceListItem dli in connectedDevices)
//			{
//				Console.WriteLine (
//					"Detected Maestro: {serialNumber=" + dli.serialNumber + 
//					", text=" + dli.text + "}");
//				goals[goalIDs[dli.serialNumber]] = new GoalFlags(new Usc(dli));
//			}
//
//            CubeRouteField field = new CubeRouteField(goals);
//
//            foreach (GoalFlags flags in goals)
//            {
//                for(int i = 0; i< 5; i++)
//                {
//                    flags.setFlagPosition(i, 0);
//                }
//            }
//                    
//
//            GoalLightsConnection conn = new GoalLightsConnection(field, "10.20.34.100", 9000, 9000);
////            GoalLightsConnection conn = new GoalLightsConnection(null, "127.0.0.1", 9001, 9000);
//            Console.WriteLine ("Running...");
//            conn.Run ();
		}

		internal class SimpleSubscriber : LCM.LCM.LCMSubscriber
		{
			public void MessageReceived(LCM.LCM.LCM lcm, string channel, LCM.LCM.LCMDataInputStream dins)
			{
				Console.WriteLine("RECV: " + channel);
				
				if (channel == "MaestroDriver/Flags")
				{
					Flags msg = new Flags(dins);
					Console.WriteLine("length1=" + msg.goals.Length);
					Console.WriteLine("length2=" + msg.goals.LongLength);
					for(int i = 0; i< 4; i++)
					{
						for(int j = 0; j < 5; j++)
						{
							Console.WriteLine ("element i=" + i + ",\t j=" + j + ", value=" + msg.goals[i,j]);
						}
					}
				}
			}
		}
	}
}
