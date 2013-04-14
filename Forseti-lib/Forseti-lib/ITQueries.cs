using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;

namespace Forseti
{
	public class ITQueries
	{
		private static string GetStringFromURL (string url)
		{
			Console.WriteLine ("Requesting " + url);
			WebRequest req = WebRequest.Create (url + 0);
			Stream stream = req.GetResponse ().GetResponseStream ();
			StreamReader reader = new StreamReader (stream);
			return reader.ReadToEnd ();
		}

		private static object GetJSONFromURL (string url)
		{
			string text = GetStringFromURL (url);
			return MiniJSON.jsonDecode (text);
		}

		public static string GetTeamConfig (int team_number)
		{
			string team_config_url_base = "http://tbp.berkeley.edu:9136/team_config/api/";
			string team_config_url = team_config_url_base + team_number;
			object data = GetJSONFromURL (team_config_url);
			try {
				Hashtable table = (Hashtable)data;
				if (!table.Contains ("file_contents")) {
					Console.WriteLine (team_config_url + " did not return the contents of a piemos config");
					return "";
				}
				Console.WriteLine ((string)table ["file_contents"]);
				return (string)table ["file_contents"];
			} catch (InvalidCastException ex) {
				Console.WriteLine ("Encountered exception " + ex + " while querying " + team_config_url);
				return "";
			}
		}

		public static List<Team> GetMatch (int match_number)
		{
			string match_url_base = "http://tbp.berkeley.edu:9136/match_schedule/api/match/";
			object data = GetJSONFromURL (match_url_base + match_number);
			Hashtable table = (Hashtable)data;
			List<Team> teams = new List<Team> ();
			Hashtable alliance1 = (Hashtable)table ["alliance1"]; 
			Hashtable alliance2 = (Hashtable)table ["alliance2"]; 
			try {
				foreach (object obj_name in alliance1.Keys) {
					int num = (int)(float)alliance1 [obj_name];
					string name = (string)obj_name;
					teams.Add (new Team (num, name));
				}
				foreach (object obj_name in alliance2.Keys) {
					int num = (int)(float)alliance2 [obj_name];
					string name = (string)obj_name;
					teams.Add (new Team (num, name));
				}
				return teams;
			} catch (InvalidCastException ex) {
				Console.WriteLine ("Encountered exception " + ex + " while querying " + match_url_base + match_number);
				return new List<Team> ();
			}
		}
		public ITQueries ()
		{
		}
	}
}

