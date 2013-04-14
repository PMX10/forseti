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

		private Hashtable lastTable;
		public Flags(
			Master master,
			int listenPort,
			int sendPort)
		{
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
//					Console.WriteLine("time=" + time);
				}
				if (this.lastTable != null)
				{
					if (this.flagAddress != null)
					{
						this.conn.SendTable(this.lastTable, this.flagAddress);
					}
				}
				
				Thread.Sleep (50);
				
			}
		}
		
		public void setFlags(ArrayList goals)
		{
			Hashtable t = new Hashtable();
			t["Type"] = "Fieldgoals";
			t["FieldGoals"] = goals;
			this.lastTable = t;
			if (this.flagAddress != null)
			{
				this.conn.SendTable(t, this.flagAddress);
			}
		}
		
		public void HashPacketReceived(Hashtable t, string senderAddress)
		{
			this.flagAddress = senderAddress;
//			Console.WriteLine("Received packet from Flags=" + MiniJSON.jsonEncode(t));
		}
	}
}

