using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;

namespace Forseti
{
	public class PiEMOSTimer
	{
		private HashConnection conn;
		private string piemosAddress;
		
		public PiEMOSTimer (string piemosAddress, int listen, int send)
		{
			this.conn = new HashConnection(listen, send);
			this.piemosAddress = piemosAddress;
		}
		
		public bool Running
		{
			get;
			set;
		}
		
		public void Start()
		{
			Thread runner = new Thread(this.Run);
			runner.Start();
		}
		
		public void Run()
		{
			long startTime = DateTime.Now.Ticks / TimeSpan.TicksPerSecond;
			
			this.conn.Start();
			this.Running = true;
			while(this.Running)
			{
				// Heartbeat
				long time = DateTime.Now.Ticks / TimeSpan.TicksPerSecond - startTime;
				Hashtable t = new Hashtable();
				t["Type"] = "Health";
				t["Uptime"] = time;
				//				Console.WriteLine("time=" + time);
				this.conn.SendTable(t, this.piemosAddress);
				Thread.Sleep (500);
			}
		}
		
		private void Send(Hashtable t)
		{
			this.conn.SendTable(t, this.piemosAddress);
		}
		
		public void SendConfigData(string configFile){
			string txt = configFile;//configText.text;
			txt = txt.Replace("\r", "").Replace("\n", "").Replace("\t", "");
			
			Hashtable table = new Hashtable();
			
			table.Add("ConfigFile", txt);
			table.Add("IsBlueAlliance", true);
			table.Add("TeamNumber", 99);
			table.Add("TeamName", "Jank");
			
			ArrayList fieldObjects = new ArrayList();//fieldObjectsText.text.arrayListFromJson();
			table.Add("FieldObjects", fieldObjects);
			
			Send(table);
		}
		
		void SendCommand(string cmd){
			Hashtable table = new Hashtable();
			table.Add("Command", cmd);
			Send(table);
		}
		
		public bool autonomous;
		public bool teleop;
		public bool robot;
		public bool halt;
		public byte matchTime;
		public string stage;
		
		void SendControlData(){
			Hashtable table = new Hashtable();
			
			Hashtable opMode = new Hashtable();
			
			opMode.Add("FieldAutonomousEnabled", autonomous);
			opMode.Add("FieldTeleopEnabled", teleop);
			opMode.Add("FieldRobotEnabled", robot);
			opMode.Add("HaltRadio", halt);
			
			table.Add("OperationMode", opMode);
			
			Hashtable match = new Hashtable();
			match.Add("Time", (float)matchTime);
			match.Add("Stage", stage);
			
			table.Add("Match", match);
			
			Send(table);
		}
	}
}

