using System;

namespace Forseti
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Starting Flagger...");

//			Flags flags = new Flags(null, 8000, 8001);
			FlagController controller = new FlagController(null);
			GoalReaders readers = new GoalReaders(null, controller, 8000, 8000);
			readers.Run ();
		}
	}
}
