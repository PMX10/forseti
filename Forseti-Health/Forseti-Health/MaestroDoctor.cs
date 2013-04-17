using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;

namespace Forseti
{
	public class MaestroDoctor : HashPacketListener
	{
		private HashConnection conn;
		private string forsetiAddress;
		
		public MaestroDoctor(string forsetiAddress, int listenPort, int sendPort)
		{
			this.field = field;
			this.forsetiAddress = forsetiAddress;
			this.conn = new HashConnection(listenPort, sendPort);
			this.conn.AddHashConPacketListener(this);
			
			this.Running = false;
		}
		
		public bool Running
		{
			get;
			set;
		}
		
		//        public void SendTagRead(Goal position, uint tagUID)
		//        {
		//            long time = DateTime.Now.Ticks / TimeSpan.TicksPerSecond;
		//            ForScoreTagRead packet = new ForScoreTagRead(position,tagUID,time);
		//            this.packetsToSend.Add(packet);
		//        }
		
		public void Start()
		{
			Thread runner = new Thread(this.Run);
			runner.Start();
		}
		
		public void Run()
		{
			this.conn.Start();
			this.Running = true;
			while(this.Running)
			{
				//                foreach (ForScoreTagRead packet in this.packetsToSend)
				//                {
				//                    this.conn.SendPacket(packet, this.forsetiAddress);
				//                }
				
				long time = DateTime.Now.Ticks / TimeSpan.TicksPerSecond;
				
				Hashtable t = new Hashtable();
				t["Uptime"] = time;
				this.conn.SendTable(t, this.forsetiAddress);
				Console.WriteLine("time=" + time);
				//                ForConHealth h = new ForConHealth(time);
				//                this.conn.SendPacket(h, this.forsetiAddress);
				Thread.Sleep (500);
			}
		}
		
		public void HashPacketReceived(Hashtable t, string senderAddress)
		{
			if (t.ContainsKey("FieldGoals"))
			{
				ArrayList boxes = (ArrayList) t["FieldGoals"];
				for(int goal = 0; goal < 4; goal++)
				{
					Console.WriteLine ("goal="  + goal);
					for(int box = 0; box < 5; box++)
					{
						Console.WriteLine ("box=" + box);
						
						//                        Console.WriteLine (boxes[5*goal + box].GetType());
						
						float value = (float) boxes[5 * goal + box];
						switch ((int) value)
						{
						case 0:
						{
							this.field.Goals[goal].SetFlagNoFlag(box);
							break;
						}
						case 1:
						{
							this.field.Goals[goal].SetFlagStandard(box);
							break;
						}
						case 2:
						{
							this.field.Goals[goal].SetFlagSpecial(box);
							break;
						}
						}
					}
				}
				
				Console.WriteLine ("received boxes=" + MiniJSON.jsonEncode(t["FieldGoals"]));
				
			}
			Console.WriteLine("received event=" + MiniJSON.jsonEncode(t));
			
			//            if (ev.Packet.Type == ForConPacketType.ForScoreLightState)
			//            {
			//                ForScoreLightStatus status = ForScoreLightStatus.FromJSON(ev.Packet.PacketString);
			//				List<BoxType> boxes = status.Goals.Goals[Goal.A].Boxes; //TODO(ajc) hardcoded, for now
			//
			//                for(int i = 0; i< 5; i++)
			//                {
			//                    double position = 0;
			//                    if(i < boxes.Count)
			//                    {
			//                        position = boxes[i] == BoxType.BoxType1 ? 1.0 : -1.0;
			//                    }
			//                    this.field.Goals[0].setFlagPosition(i, position);
			//                }
			//            }
		}
	}
}

