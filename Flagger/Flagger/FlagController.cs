using System;
using System.Collections;
using System.Collections.Generic;

namespace Forseti
{
	/// <summary>
	/// Flag controller accepts tag reads from the GoalReader, actuates flags via Flags.
	/// </summary>
	public class FlagController
	{
		private Flags flags;

		private ArrayList boxes;
		private int current;

		public FlagController (Flags flags)
		{
			this.flags = flags;
			this.boxes = new ArrayList();
			for(int i = 0; i<20; i++)
			{
				boxes.Add(0);
			}
			current = 0;
		}

		public void TagRead(string goal, uint tag)
		{
			Console.WriteLine ("tag read: goal=" + goal + ",\t tag=" + tag);
			boxes[current++] = 1;
			this.flags.setFlags(this.boxes);
		}
	}
}

