namespace PiE.Net
{
    using System;
    using System.Collections.Generic;
    using System.Net;
    using System.Net.Sockets;
    using System.Text;
    using System.Threading;
#if UNITY_EDITOR
    using UnityEngine;
#endif
    
    /// <summary>
    /// UDP socket abstraction.
    /// </summary>
    public class UDPSocket
    {
        /// <summary>
        /// Indicates when this.AcceptCallback() has been called.
        /// Used by this.Run()  to not only process
        /// a single connection accept at once.
        /// </summary>
        private ManualResetEvent acceptCalled = new ManualResetEvent(false);
        
        /// <summary>
        /// The socket.
        /// </summary>
        private UdpClient socket;
        
        /// <summary>
        /// The IPendpoint of the UDP endpoint.
        /// </summary>
        private IPEndPoint endpoint;
        
        /// <summary>
        /// The connection port of UDP endpoint.
        /// </summary>
        private int listenPort;
        private int sendPort;
        
        /// <summary>
        /// Listeners of
        /// </summary>
        private List<UDPSocketDataCallback> listeners;
        
        /// <summary>
        /// Initializes a new instance of the <see cref="PiE.Net.UDPSocket"/> class.
        /// </summary>
        /// <param name='address'>
        /// PiEMOS Client's address.
        /// </param>
        /// <param name='port'>
        /// Port of the PiEMOS client.
        /// </param>
        public UDPSocket(int listenPort, int sendPort)
        {
            this.listenPort = listenPort;
            this.sendPort = sendPort;
            this.endpoint = new IPEndPoint(IPAddress.Any, listenPort);
            this.socket = new UdpClient(listenPort);
			this.socket.Client.ReceiveBufferSize = 0;
            this.listeners = new List<UDPSocketDataCallback>();
        }
        
        /// <summary>
        /// Data callback, the type to call on data receive.
        /// See this.AddDataReceiver().
        /// </summary>
        /// <param name="data">
        /// The received data.
        /// </param>
        public delegate void UDPSocketDataCallback(byte[] data, string senderAddress);
        
        /// <summary>
        /// Gets or sets a value indicating whether this <see cref="PiE.Net.UDPSocket"/> is running.
        /// </summary>
        /// <value>
        /// <c>true</c> if running; otherwise, <c>false</c>.
        /// </value>
        public bool Running
        {
            get;
            set;
        }
        
        public void Send(byte[] byteData, string address)
        {
            this.socket.Send(byteData, byteData.Length, address, this.sendPort);
        }
        
        /// <summary>
        /// Start this instance.
        /// </summary>
        public void Start()
        {
#if !UNITY_EDITOR
            new Thread(this.Run).Start();
#endif
        }
        
        public void Poll(){
            while(this.socket.Available > 0){
                IPEndPoint ep = null;
                byte[] bytes = this.socket.Receive(ref ep);
                
                ReadCallbackBlocking(bytes, ep.Address);
            }
        }
        
        
        /// <summary>
        /// Run this instance.
        /// </summary>
        public void Run()
        {
            this.Running = true;
            while (this.Running)
            {
                // Resets acceptCalled-- if we're here, this.AcceptCallback() has been called.
                this.acceptCalled.Reset();
                
                // Begins receiving a datagram from a remote host asynchronously.
                // does not block.
                this.socket.BeginReceive(this.ReadCallback, null);
                
                // Waits until a connection is made before continuing.
                this.acceptCalled.WaitOne();
            }
        }
        
        /// <summary>
        /// Adds the data receiver, to be notified on data receive.
        /// Notified at this.notifyReceive().
        /// </summary>
        /// <param name='cb'>
        /// The callback to call on data receive.
        /// </param>
        public void AddDataReceiver(UDPSocketDataCallback cb)
        {
            this.listeners.Add(cb);
        }
        
        /// <summary>
        /// Removes the data receiver, to from being notified on data receive.
        /// </summary>
        /// <param name='cb'>
        /// The callback to call on data receive, that was registered with this.AddDataReciever().
        /// </param>
        public void RemoveDataReceiver(UDPSocketDataCallback cb)
        {
            this.listeners.Remove(cb);
        }
        
        /// <summary>
        /// Reads the callback.
        /// </summary>
        /// <param name='ar'>
        /// The result of the asynchronous operation.
        /// </param>
        private void ReadCallback(IAsyncResult ar)
        {
            // Signals the this.Run() thread to continue.
            this.acceptCalled.Set();
            
            byte[] received = this.socket.EndReceive(ar, ref this.endpoint);
            
            this.NotifyReceive(received, this.endpoint.Address.ToString());
        }
        
        private void ReadCallbackBlocking(byte[] received, IPAddress address){
            this.NotifyReceive(received, address.ToString());
        }
        
        /// <summary>
        /// Notifies listeners that a SocketServerConnection has received data.
        /// Called by ServerSocketConnections which are children of this SocketServer.
        /// </summary>
        /// <param name='received'>
        /// The byte buffer of received data.
        /// </param>
        private void NotifyReceive(byte[] received, string senderAddress)
        {
            foreach (UDPSocketDataCallback cb in this.listeners)
            {
                cb(received, senderAddress);
            }
        }
    }
}