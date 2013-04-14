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
		private Goals goals;
		private int current;
		
		private Dictionary<string, int> goalStringToPosition;
		private BoxMapping mapping;

		public FlagController (Flags flags, BoxMapping mapping)
		{
			this.goals = new Goals();
			this.flags = flags;
			this.boxes = new ArrayList();
			for(int i = 0; i<20; i++)
			{
				boxes.Add(0);
			}
			current = 0;

			this.goalStringToPosition = new Dictionary<string, int>();
			this.goalStringToPosition["A"] = 0;
			this.goalStringToPosition["B"] = 1;
			this.goalStringToPosition["C"] = 2;
			this.goalStringToPosition["D"] = 3;
			this.goalStringToPosition["VerifyA"] = 10;
			this.goalStringToPosition["VerifyB"] = 11;
			this.goalStringToPosition["VerifyC"] = 12;
			this.goalStringToPosition["VerifyD"] = 13;
			this.goalStringToPosition["Dispense"] = 8;
			this.goalStringToPosition["Unknown"] = 9;

			this.mapping = mapping;
		}

		public void TagRead(string goal, uint tag)
		{
			int boxVal = 0;
			switch(this.mapping.GetEffect((int)tag))
			{
			case "add":
			{
				boxVal = 1;
				break;
			}
			case "multiply":
			{
				boxVal = 2;
				break;
			}
			}
			this.goals.PushBox(this.goalStringToPosition[goal], boxVal);
			Console.WriteLine ("tag read: goal=" + goal + ",\t tag=" + tag + ",\t value=" + boxVal);
			
//			boxes[current++] = 1;
//			if(current == 20)
//			{
//				current = 0;
//				for(int i = 0; i<20; i++)
//				{
//					boxes.Add(0);
//				}
//			}
			this.flags.setFlags(this.goals.toArrayList());
		}
	}
}

