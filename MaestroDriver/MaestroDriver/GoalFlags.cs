using System;
using Pololu.Usc;
using Pololu.UsbWrapper;

namespace Forseti
{
	public class GoalFlags
	{

		private ushort[][] values = new ushort[][] {
			new ushort[] {6000, 6000, 6000, 6000, 6000},
            new ushort[] {2200, 9500, 2200, 9500, 2200},
            new ushort[] {9500, 2200, 9500, 2200, 9500}};

//		private ushort[][] values = new ushort[][] {
//			new ushort[] {6000, 6000, 6000, 6000, 6000},
//			new ushort[] {4000, 4000, 4000, 4000, 4000},
//			new ushort[] {8000, 8000, 8000, 8000, 8000}};

		private Usc maestro;

		public GoalFlags (Usc maestro)
		{
			this.maestro = maestro;
		}

		public void SetFlagNoFlag(int flag)
		{
			Console.WriteLine ("set noflag target=" + this.values[0][flag]);
			this.maestro.setTarget((byte)flag, this.values[0][flag]);
		}

		public void SetFlagStandard(int flag)
		{
			Console.WriteLine ("set standard target=" + this.values[1][flag]);
			this.maestro.setTarget((byte)flag, this.values[1][flag]);
			
		}

		public void SetFlagSpecial(int flag)
		{
			Console.WriteLine ("set special target=" + this.values[2][flag]);
			this.maestro.setTarget((byte)flag, this.values[2][flag]);
		}

		public void setFlagPosition(int flag, double position)
		{
            Console.WriteLine("setting flag: flag=" + flag + ", position=" + position);
            int range = (int) (this.values[2][flag] - this.values[1][flag]);
            ushort retu = (ushort) ((position * range) / 2.0 + this.values[0][flag]);
            this.maestro.setTarget((byte) flag, retu);
		}
	}
}

