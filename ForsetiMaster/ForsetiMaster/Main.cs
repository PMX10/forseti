using System;

namespace ForsetiMaster
{
	class MainClass
	{
		public static void Main (string[] args)
		{
			Console.WriteLine ("Starting Forseti Master...");
			Master m = new Master(5000, 5001);
			m.Run ();
		}
	}
}
