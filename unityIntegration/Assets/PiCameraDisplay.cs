using System.Collections.Concurrent;
using System.Threading;
using NetMQ;
using UnityEngine;
using NetMQ.Sockets;
using System.Diagnostics;
using UnityEngine.UI;

public class PiCameraDisplay : MonoBehaviour
{


    // The hardcoded (for now) pi IP and port
    private int port;
    private int offset = 10000;
    private string serverIP = "tcp://ec2-13-58-201-148.us-east-2.compute.amazonaws.com:";


    Texture2D camTexture;

    RawImage screenDisplay;

    Canvas canvas;

    // This is an object that spins up a thread to manage the socket connection
    //and then hands off the data to a "messageDelegate" that handles the data
    //in this instance the "messageDelegate" is the HandleMessage function
    private NetMqListener _netMqListener;

    // Script Start
    private void Start()
    {
		
        port = DropDownMenu.port;
        UnityEngine.Debug.Log(port);
        
        //initialize cam texture and get the raw image
        this.camTexture = new Texture2D(2, 2);
        this.screenDisplay = GetComponent<RawImage>();
        this.canvas = GetComponent<Canvas>();

        // Create and start listener object
        _netMqListener = new NetMqListener(HandleMessage, serverIP + (port + offset));
        _netMqListener.Start();
    }

    // This function handles the message
    // This is where we should put logic to display the image
    private void HandleMessage(byte[] message)
    {
        this.camTexture.LoadImage(message);
        screenDisplay.texture = camTexture;
        Canvas.ForceUpdateCanvases();
    }

    // When our scripts update function is called, we update the listener
    private void Update()
    {
        _netMqListener.Update();
    }

    // Stop the listener on program halt
    private void OnDestroy()
    {
        _netMqListener.Stop();
    }
}

// This is an object that spins up a thread to manage the socket connection
//and then hands off the data to a "messageDelegate" that handles the data
//in this instance the "messageDelegate" is the HandleMessage function
public class NetMqListener
{
    // The listenerWorker is a thread that manages the subscriber socket
    //and updates the message queue
    private readonly Thread _listenerWorker;

    //This boolean tells the listenerwoker when to stop receiving (ie true == STOP)
    private bool _listenerCancelled;

    // This is a function passed in that we hand off received data to
    // see https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/
    // for information about delegates
    public delegate void MessageDelegate(byte[] message);
    private readonly MessageDelegate _messageDelegate;

    // This is a queue that contains all the data that still needs to be handed off
    private readonly ConcurrentQueue<byte[]> _messageQueue = new ConcurrentQueue<byte[]>();

    // Pi's server ip address and port number
    private string serverIP;

    // Listener object constuctor
    public NetMqListener(MessageDelegate messageDelegate, string serverIPin)
    {
        // Assign IP and port
        serverIP = serverIPin;

        //Read in delegate function and spin up listener thread
        _messageDelegate = messageDelegate;
        _listenerWorker = new Thread(ListenerWork);
    }

    // Start the listener thread
    public void Start()
    {
        _listenerCancelled = false;
        _listenerWorker.Start();
    }


    // Thread function that handles the socket connection and reads in data
    private void ListenerWork()
    {
        AsyncIO.ForceDotNet.Force();
        // Create new sub socket
        using (var subSocket = new SubscriberSocket())
        {
            //High watermark is the number of messages that will be kept in memory
            //until the socket enters exception state and drops or blocks messages
            //at setting 1000 there is no limit...
            subSocket.Options.ReceiveHighWatermark = 1;

            //connect socket with IP
            subSocket.Connect(this.serverIP);

            //socket.subscribe(topic) 
            //Because we don't care about having a topic we send 
            // "" to subscribe to all topics
            subSocket.Subscribe("");

            // Loop until cancel
            while (!_listenerCancelled)
            {
                //keep trying to read in data until we "hear something"
                byte[] frameBytes;
                if (!subSocket.TryReceiveFrameBytes(out frameBytes)) continue;

                //print out findings to Log
                //Prolly remove this later...
                //UnityEngine.Debug.Log(frameBytes.ToString());

                //Enqueue data into list to be handled
                _messageQueue.Enqueue(frameBytes);
            }
            //After being cancelled, close socket connection and cleanup config
            subSocket.Close();
        }
        NetMQConfig.Cleanup();
    }

    // This method is called on scripts update function
    public void Update()
    {
        // If message queue is empty we're caught up, otherwise
        // loop through until we have processed all messages
        while (!_messageQueue.IsEmpty)
        {
            // Try to take data out of queue and pass to our delegate
            byte[] message;
            if (_messageQueue.TryDequeue(out message))
            {
                _messageDelegate(message);
            }
            else
            {
                break;
            }
        }
    }

    // Stops the listener thread
    public void Stop()
    {
        _listenerCancelled = true;
        _listenerWorker.Join();
    }
}
