using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;

namespace Forseti
{
	public class GoalReaders : HashPacketListener
	{
		private HashConnection conn;
		
		private string readerAddress;
						
		private Master master;
		private FlagController controller;

		private uint prevTag;
		
		public GoalReaders(Master master,FlagController controller, int listenPort, int sendPort)
		{
			this.master = master;
			this.controller = controller;
			this.conn = new HashConnection(listenPort, sendPort);
			this.conn.AddHashConPacketListener(this);
			//this.previousSentTag = 999;
			this.Running = false;
			prevTag = 0;
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
				if (this.readerAddress != null)
				{
					this.conn.SendTable(t, this.readerAddress);
				}
				Thread.Sleep (500);
			}
		}
		
		public void HashPacketReceived(Hashtable t, string senderAddress)
		{
//			Console.WriteLine ("received from address=" + senderAddress + ", table=" + MiniJSON.jsonEncode(t));
			this.readerAddress = senderAddress;
			if (t.ContainsKey("Type") && t["Type"].Equals("Health"))
			{
				//                string readersJson = t.ContainsKey ("Readers") ? (string) t["Readers"] : null;
				//                Hashtable readers = (Hashtable) MiniJSON.jsonDecode(readersJson);
				Hashtable readers = (Hashtable) t["Readers"];
				
				//                Console.WriteLine ("A=" + readers["A"]);
				//                Console.WriteLine ("B=" + readers["B"]);
				//                Console.WriteLine ("C=" + readers["C"]);
				//                Console.WriteLine ("D=" + readers["D"]);
				//                Console.WriteLine ("VerifyA=" + readers["VerifyA"]);
				//                Console.WriteLine ("VerifyB=" + readers["VerifyB"]);
				//                Console.WriteLine ("VerifyC=" + readers["VerifyC"]);
				//                Console.WriteLine ("VerifyD=" + readers["VerifyD"]);
				//                Console.WriteLine ("Dispense=" + readers["Dispense"]);
				//                Console.WriteLine ("Unknown=" + readers["Unknown"]);
				//                Console.WriteLine ("Time=" + t["Time"]);
			} else if (t.ContainsKey("Type") && t["Type"].Equals("TagRead"))
			{
//				Console.WriteLine ("Reader=" + t["Reader"]);
//				Console.WriteLine ("TagID=" + t["TagID"]);
//				Console.WriteLine ("Time=" + t["Time"]);
				this.NotifyListeners((string)t["Reader"], uint.Parse ((string)t["TagID"]));
				
				//sends tagconfirm
				Hashtable confirm = new Hashtable();
				confirm["Type"] = "Confirm";
				confirm["Reader"] = t["Reader"];
				confirm["TagID"] = t["TagID"];
				confirm["Time"] = t["Time"];
				this.conn.SendTable(confirm, this.readerAddress);

			}
			
			//            this.readerAddress = ev.SenderAddress;
			//            //Console.WriteLine("Received ForScorePacket event=" + ev);
			//            if (ev.Packet.Type == ForConPacketType.ForScoreTagRead)
			//            {
			//                ForScoreTagRead readpack = ForScoreTagRead.FromJSON(ev.Packet.PacketString);
			//
			//                // Only notifies listeners if we haven't just sent it.
			//                if (this.previousSentTag != readpack.TagUID)
			//                {
			//                    this.previousSentTag = readpack.TagUID;
			//                    this.NotifyListeners(readpack.Position, readpack.TagUID);
			//                }
			//
			//                // Sends a confirm packet to notify the GoalReader to stop spamming
			//                ForScoreTagConfirm confirm = new ForScoreTagConfirm(
			//                    readpack.Position,
			//                    readpack.TagUID,
			//                    readpack.Time);
			//                this.conn.SendPacket(confirm, this.readerAddress);
			//            }
		}
		
		private void NotifyListeners(string position, uint tag)
		{
			if (prevTag != tag)
			{
				this.controller.TagRead(position, tag);
			}
			prevTag = tag;
//			GoalReadEvent ev = new GoalReadEvent(position, tag);
//			foreach (IGoalReaderListener l  in this.master.GoalReaderListeners)
//			{
//				l.tagAppeared(ev);
//			}
		}
	}
}

