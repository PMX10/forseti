using System;
using System.Collections;
using System.Threading;
using Forseti;

namespace ForsetiMasterTest
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Hello World!");
			HashConnection conn = new HashConnection(5001, 5000);
			conn.Start();
			Hashtable t = new Hashtable();
			t["Type"] = "Register";
			t["Name"] = "Tester";
			t["IP"] = "8.8.8.8";
			t["Port"] = 6000;
			while(true)
			{
				Console.WriteLine ("Sending table...");
				conn.SendTable(t, "127.0.0.1");
				Thread.Sleep(500);
			}
		}
	}
}
