using System;
using System.Collections;
using System.Collections.Generic;


namespace Forseti
{
	public class BoxMapping
	{			
		private Dictionary<int, int> effect;
		private int ADD = 1;
		private int MULTIPLY = 2;

		public BoxMapping ()
		{
			effect = new Dictionary<int, int> ();
		}

		public string GetEffect (int tag_id)
		{
			if (effect.ContainsKey (tag_id)) {
				if (effect [tag_id] == ADD) {
					return "add";
				} else if (effect [tag_id] == MULTIPLY) {
					return "multiply";
				}
			}
			return "Unknown";
		}

		public ArrayList GetObjects ()
		{
			string filename = "../../../../resources/field_mapping.json";
			try {
				System.IO.StreamReader file = new System.IO.StreamReader (filename);
				object data = MiniJSON.jsonDecode (file.ReadToEnd ());
				return (ArrayList)data;
			} catch (InvalidCastException ex) {
				Console.WriteLine ("Could not parse " + filename + ", encountered error " + ex);
				return new ArrayList ();
			}
		}

		public BoxMapping Load ()
		{
			try {
				ArrayList list = GetObjects ();
				foreach (object read_obj in list) {
					Hashtable read = (Hashtable)read_obj;
					if (read.Contains ("tagId") && read.Contains ("objectType")) {
						int t = (int)(float)read ["objectType"];
						int tag_id = Convert.ToInt32 ((string)read ["tagId"]);
						effect [tag_id] = t;
					}
				} 
			} catch (InvalidCastException ex) {
				Console.WriteLine ("Could not parse field mapping got exception " + ex);
			} 
			return this;
		}
	}
}

