using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;

namespace Forseti
{
	public class Flags : HashPacketListener
	{
		
		private HashConnection conn;
		private string flagAddress;
		
		private Master master;
		
		public Flags(
			Master master,
			int listenPort,
			int sendPort)
		{
			this.master = master;
//			this.master.AddFieldGoalsChangeListener(this);
			this.conn = new HashConnection(listenPort, sendPort);
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
			while(this.Running)
			{
				if (flagAddress != null)
				{
					long time = DateTime.Now.Ticks / TimeSpan.TicksPerSecond;
					Hashtable t = new Hashtable();
					t["Uptime"] = time;
					this.conn.SendTable(t, this.flagAddress);
					Console.WriteLine("time=" + time);
				}
				
				Thread.Sleep (500);
				
			}
		}
		
		public void setFlags(ArrayList goals)
		{
			Hashtable t = new Hashtable();
			t["Type"] = "Fieldgoals";
			t["FieldGoals"] = goals;
			if (this.flagAddress != null)
			{
				this.conn.SendTable(t, this.flagAddress);
			}
		}
		
		public void HashPacketReceived(Hashtable t, string senderAddress)
		{
			this.flagAddress = senderAddress;
			Console.WriteLine("Received packet from Flags=" + MiniJSON.jsonEncode(t));
		}
	}
}

