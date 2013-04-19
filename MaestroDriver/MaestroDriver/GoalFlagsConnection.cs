using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using LCM.LCM;

namespace Forseti
{
	public class GoalFlagsConnection : LCM.LCM.LCMSubscriber
    {

        private CubeRouteField field;
		private LCM.LCM.LCM lcm;
        
        public GoalFlagsConnection(LCM.LCM.LCM lcm, CubeRouteField field)
        {
			this.lcm = lcm;
            this.field = field;
			this.lcm.Subscribe("MaestroDriver/Flags", this);
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
            this.Running = true;
			double start = ((double)DateTime.Now.Ticks) / (double)TimeSpan.TicksPerSecond;
            while(this.Running)
            {
                double time = ((double)DateTime.Now.Ticks) / (double)TimeSpan.TicksPerSecond;

				Health msg = new Health();
				msg.uptime = time - start;
				this.lcm.Publish("MaestroDriver/Health", msg);
                Thread.Sleep (250);
            }
        }

		public void MessageReceived(LCM.LCM.LCM lcm, string channel, LCM.LCM.LCMDataInputStream dins)
		{
			Console.WriteLine("RECV: " + channel);
			
			if (channel == "MaestroDriver/Flags")
			{
				Flags msg = new Flags(dins);
				Console.WriteLine("length1=" + msg.goals.Length);
				Console.WriteLine("length2=" + msg.goals.LongLength);
				for(int goal = 0; goal< 4; goal++)
				{
					for(int box = 0; box < 5; box++)
					{
						Console.WriteLine ("element goal=" + goal + ",\t box=" + box + ", value=" + msg.goals[goal,box]);
						this.field.Goals[goal].setFlagPosition(box, msg.goals[goal, box]);
					}
				}
			}
		}
    }
}

