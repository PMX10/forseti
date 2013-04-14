using System;
using System.Collections;

namespace Forseti
{
	public interface HashPacketListener
	{
		void HashPacketReceived(Hashtable t, string senderAddress);
	}
}

