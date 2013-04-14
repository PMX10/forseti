using System;
using System.Collections;
using System.Threading;

namespace Forseti
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Starting Flagger...");

			BoxMapping mapping = new BoxMapping ().Load ();

			Flags flags = new Flags (null, 9000, 9000);
			flags.Start ();
			ArrayList l = new ArrayList ();
			for (int i = 0; i< 20; i++) {
				l.Add (0);
			}
			Thread.Sleep (2000);
			flags.setFlags (l);
//			while(true)
//			{
//				ArrayList l = new ArrayList ();
//				for (int i = 0; i< 20; i++) {
//					l.Add (1);
//				}
//				flags.setFlags (l);
//				Thread.Sleep (500);
//			}
			
			FlagController controller = new FlagController (flags, mapping);
			GoalReaders readers = new GoalReaders (null, controller, 8000, 8000);
			Console.WriteLine ("Running...");
			readers.Run ();
//			Goals g = new Goals();
//			g.PushBox(0, 1);
//			g.PushBox(0, 1);
//			g.PushBox(0, 1);
//			g.PushBox(0, 1);
//
//			g.PushBox(1, 2);
//			g.PushBox(2, 1);
//			
//			Console.WriteLine (MiniJSON.jsonEncode(g.toArrayList()));

		}
	}
}
