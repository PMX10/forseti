using System;

namespace Forseti
{
	/// <summary>
	/// Flag controller accepts tag reads from the GoalReader, actuates flags via Flags.
	/// </summary>
	public class FlagController
	{
		private Flags flags;

		public FlagController (Flags flags)
		{
			this.flags = flags;
		}

		public void TagRead(string goal, uint tag)
		{
			Console.WriteLine ("tag read: goal=" + goal + ",\t tag=" + tag);
		}
	}
}

