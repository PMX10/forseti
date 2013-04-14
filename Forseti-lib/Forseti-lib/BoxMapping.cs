using System;
using System.Collections;
using System.Collections.Generic;


namespace Forseti
{
	public class BoxMapping
	{			
		private Dictionary<int, string> effect;

		public BoxMapping ()
		{
			effect = new Dictionary<int, string> ();
		}

		public string GetEffect (int tag_id)
		{
			if (effect.ContainsKey (tag_id)) {
				return effect [tag_id];
			} else {
				return "Unknown";
			}
		}

		public BoxMapping Load ()
		{
			string filename = "../../../../resources/field_mapping.json";
			System.IO.StreamReader file = new System.IO.StreamReader (filename);
			object data = MiniJSON.jsonDecode (file.ReadToEnd ());
			try {
				ArrayList list = (ArrayList)data;
				foreach (object read_obj in list) {
					Hashtable read = (Hashtable)read_obj;
					if (read.Contains ("tagId") && read.Contains ("effect")) {
						string e = (string)read ["effect"];
						int tag_id = Convert.ToInt32 ((string)read ["tagId"]);
						effect [tag_id] = e;
					}
				} 
			} catch (InvalidCastException ex) {
				Console.WriteLine ("Could not parse field mapping got exception " + ex);
			} 
			return this;
		}
	}
}

