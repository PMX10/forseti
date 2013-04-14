namespace Forseti
{
	using System;
	using System.Collections;
	using System.Collections.Generic;
	using PiE.Net;
	
	/// <summary>
	/// HashConnection is a transport for exchanging hashtables,
	/// transmitted over UDP using JSON.
	/// 
	/// </summary>
	public class HashConnection
	{
		private UDPSocket client;
		
		private List<HashPacketListener> listeners;
		
		public HashConnection(int listenPort, int sendPort)
		{
			this.client = new UDPSocket(listenPort, sendPort);
			this.client.AddDataReceiver(this.bytesReceived);
			this.listeners = new List<HashPacketListener>();
		}
		
		public bool Running
		{
			get
			{
				return this.client.Running;
			}
			set
			{
				this.client.Running = value;
			}
		}
		
		public void Start()
		{
			this.client.Start();
		}
		
		public void SendTable(Hashtable table, string address)
		{
//			Console.WriteLine ("Sending=" + MiniJSON.jsonEncode(table));
			byte[] data = System.Text.Encoding.ASCII.GetBytes(MiniJSON.jsonEncode(table));
			this.client.Send(data, address);
		}
		
		public void bytesReceived(byte[] bytes, string senderAddress)
		{
			if(bytes[0] != 0) //throw out malformed packets
			{
				string jsonstring = System.Text.Encoding.ASCII.GetString (bytes);
				//                Console.WriteLine ("received string=" +  jsonstring);
				//                JsonSerializer<Hashtable> seralize = new JsonSerializer<Hashtable>();
				//                Hashtable received = seralize.DeserializeFromString(jsonstring);
				Hashtable received = (Hashtable) MiniJSON.jsonDecode(jsonstring);
				if (received != null)
				{
					this.notifyListeners(received, senderAddress);
				}
			}
		}
		
		private void notifyListeners(Hashtable packet, string sender)
		{
			foreach (HashPacketListener l in this.listeners)
			{
				l.HashPacketReceived(packet, sender);
			}
		}
		
		public void AddHashConPacketListener(
			HashPacketListener l)
		{
			this.listeners.Add(l);
		}
		
		public void RemoveHashConPacketListener(
			HashPacketListener l)
		{
			this.listeners.Remove(l);
		}
	}
}