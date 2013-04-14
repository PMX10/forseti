using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;

namespace Forseti
{
	public class PiEMOSTimer : HashPacketListener
	{
		private HashConnection conn;
		private string piemosAddress;

		private const int AutonomousStageLength = 20; //seconds
		
		private const int TeleopStageLength = 100; //seconds
		
		private long fieldTime = 0;
						
		public PiEMOSTimer (string piemosAddress, int listen, int send)
		{
			this.conn = new HashConnection(listen, send);
			this.conn.AddHashConPacketListener(this);
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
//				Hashtable t = new Hashtable();
//				t["Type"] = "Health";
//				t["Uptime"] = time;
				Console.WriteLine("time=" + time);
//				this.conn.SendTable(t, this.piemosAddress);


				// match control
				matchTime = (byte) time;
				if( matchTime < AutonomousStageLength)
				{
					this.stage = "Autonomous";
					autonomous = true;
					teleop = false;
				} else if (matchTime < TeleopStageLength)
				{
					this.stage = "Teleop";
					autonomous = false;
					teleop = true;
				}
				robot = true;
				halt = false;
				SendControlData();
				
				Thread.Sleep (500);
			}
		}
		
		public void HashPacketReceived (Hashtable t, string senderAddress)
		{
			if (t.ContainsKey("Health"))
			{
				Hashtable payload = (Hashtable) t["Health"];
				string piemos_state = (string)payload["PiEMOSState"];
				if(piemos_state.Equals ("MatchStartWaiting"))
				{
					Console.WriteLine ("Config Received!!!!!!!!");
//					done = true;
				}
			}
		}
		
		private void Send(string name, Hashtable t)
		{
			Hashtable wrapper = new Hashtable();
			wrapper[name] = t;
			this.conn.SendTable(wrapper, this.piemosAddress);
		}
		
		private void Send( Hashtable t)
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
			
			Send("ConfigData",table);
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
			
			Send("ControlData", table);
		}
	}
}

