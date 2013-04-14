using System;
using System.Collections;

namespace Forseti
{
	public class Goals
	{
		private ArrayList[] lists;

		public Goals ()
		{
			this.lists = new ArrayList[4];
			for(int i = 0; i<lists.Length; i++)
			{
				lists[i] = new ArrayList();
			}
		}

		public void PushBox(int goal, int status)
		{
			if(goal < lists.Length)
			{
//				lists[goal].Insert (0, status);
				lists[goal].Add(status);
			}
		}

		public ArrayList toArrayList()
		{
			ArrayList retu = new ArrayList();

			foreach (ArrayList list in lists)
			{
				for(int box=0; box<5; box++)
				{
//					// a box doesn't exist
					if(list.Count <= box)
					{
						retu.Add(0);

					} else 
					{
//						retu.Add (1);
						retu.Add ((int) list[box]);
					}
				}
			}
			return retu;
		}
	}
}

