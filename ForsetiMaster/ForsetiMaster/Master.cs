using System;
using System.Threading;
using System.Collections;
using System.Collections.Generic;
using Forseti;

namespace ForsetiMaster
{
	/**
	 * A nameserver.
	 * Accepts whoami packets, and responds to requests for such information
	 */
	public class Master : HashPacketListener
	{
		private HashConnection conn;

		public Master (int listenPort, int sendport)
		{
			this.conn = new HashConnection(listenPort, sendport);
			this.conn.AddHashConPacketListener(this);
		}

		public bool Running
		{
			get;
			set;
		}

		public void Start()
		{
			Thread runner = new Thread(this.Run);
			runner.Start ();
		}

		public void Run()
		{
			this.conn.Start ();
			this.Running = true;
		}

		public void HashPacketReceived (Hashtable t, string senderAddress)
		{
			Console.WriteLine ("Received packet!");
			if (t.ContainsKey("Type") && t["Type"].Equals ("Register"))
			{
				string name = (string) t["Name"];
				string ip = (string) t["IP"];
				float port =  (float) t["Port"];
				Console.WriteLine ("name=" + name +  ",\t ip=" + ip +",\t port=" + port);
			}
		}
	}
}

