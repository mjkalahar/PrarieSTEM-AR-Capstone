using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using UnityEngine.UI;
using NetMQ.Sockets;
using NetMQ;
using System.Threading;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json;

/**
* Class for controlling and updating the information of the dropdown in the main menu for selecting a video feed
*/ 
public class DropDownMenu : MonoBehaviour
{
	private int _listeningPort = 5051;
    private string _serverIP = "tcp://ec2-54-164-70-144.compute-1.amazonaws.com:";
	//Options is the list of strings that is shown to the user
	List<string> options = new List<string>{"Searching, please wait"};
	List<int> ports = new List<int>{};
	private static string _json = "[]";
	
	//Menu is the "game component"
	Dropdown menu;
	//Pi's port number
	public static int port = -1;

	// This is an object that spins up a thread to manage the socket connection
    //and then hands off the data to a "messageDelegate" that handles the data
    //in this instance the "messageDelegate" is the UpdateList function
	private PiNameGetter _piNameGetter;

    /**
    * Start is called before the first frame update
    * Attempt to set up our dropdown and create a listener for updating information
    */ 
    void Start()
    {
		//Grab component that this script is attached to
		menu = GetComponent<Dropdown>();
		//Clean it out
		menu.ClearOptions();
		//Add our options
		menu.AddOptions(options);
		//We pass it our function so that port will be changed on select
		menu.onValueChanged.AddListener(delegate {
			menuChange(menu);
		});

		Debug.Log("Searching for " + _serverIP + _listeningPort);

		_piNameGetter = new PiNameGetter(UpdateList, _serverIP + _listeningPort);
		_piNameGetter.Start();
    }

    /**
    * Update is called every frame
    * Grab the new json and attempt to parse it into a usable drop down
    */ 
    void Update()
    {
		int v = menu.value;
		JArray arr = new JArray();
		//Try to deserialize first
		try
		{
			var deserialized = JsonConvert.DeserializeObject<string>(_json);
			arr = JArray.Parse(deserialized);
		}
		//Deserialize fails
		catch(Exception e)
        {
			//Try to use direct json
			try
            {
				arr = JArray.Parse(_json);
			}
			//Invalid json we can't handle
			catch(Exception ee)
            {
				
            }
        }
		//clear lists
		options = new List<string>{"Please select a Pi"};
		ports = new List<int>{-1};
		
		bool isEmpty = true;
		//iterate through arr
		foreach (JObject pi in arr)
		{
			isEmpty = false;
			options.Add((string) pi.GetValue("Name"));
			ports.Add(int.Parse((string) pi.GetValue("Port")));
		}
		
		//if list is empty then display no availible pis
		if (isEmpty)
		{
			options = new List<string>{"No pi's found!"};
		}
		menu.ClearOptions();
		menu.AddOptions(options);
		menu.value = v;
    }
	
	/**
    * OnDestroy is called when game object is destroyed
    * Stop our listener
    */ 
	void OnDestroy()
	{
		_piNameGetter.Stop();
	}
	
	/**
    * When dropdown value is changed, update the current port to the port selected
    */ 
	void menuChange(Dropdown change){
		port = ports[change.value];
	}
	
	/**
    * This is the message delegate that the listening thread will use to update the list
    */ 
	void UpdateList(string message)
	{
		_json = message;
	}
}

/**
* Class for handling incoming connection from server
*/ 
public class PiNameGetter
{
	private readonly Thread _nameGetterWorker;
	private bool _nameGetterCancelled;
	
	public delegate void MessageDelegate(string message);
	private readonly MessageDelegate _messageDelegate;
	
	private string _serverIP;
	private string _newJsonString = "";
	private string _jsonString = "";
	
	/**
	* Intialize our listener
	* @param messageDelegate Delegate function to be called when we receive a new message
	* @param serverIPin IP Address of the server we are going to attempt to find connections on
	*/ 
	public PiNameGetter(MessageDelegate messageDelegate, string serverIPin)
	{
		_serverIP = serverIPin;
		
		_messageDelegate = messageDelegate;
		_nameGetterWorker = new Thread(nameGetterWork);
	}

	/**
	* Start the listener
	*/
	public void Start()
	{
		_nameGetterCancelled = false;
		_nameGetterWorker.Start();
	}
	
	/**
	* Performs actual task of connecting to server and attempting to retreive JSON information about connections
	*/
	private void nameGetterWork()
	{
		AsyncIO.ForceDotNet.Force();

		//Subscriber socket, connect to server and listen
		using (var subSocket = new SubscriberSocket())
		{
			subSocket.Options.ReceiveHighWatermark = 1;
			subSocket.Connect(_serverIP);
			subSocket.Subscribe("");
			
			//While still running
			while (!_nameGetterCancelled)
			{
				//Attempt to grab a string from server
				if (!subSocket.TryReceiveFrameString(out _newJsonString)) continue;
				
				//If the string is not equal to the previous string, we have an update
				if (!_newJsonString.Equals(_jsonString))
				{
					//Assign the new string as our current string, then forward our message to the messageDelegate function
					Debug.Log("New JSON is " + _newJsonString);
					_jsonString = _newJsonString;
					_messageDelegate(_jsonString);
				}
			}
			//Close socket
			subSocket.Close();
		}
		//Cleanup
		NetMQConfig.Cleanup();
	}

	/**
	* Stops the listener
	*/
	public void Stop()
	{
		_nameGetterCancelled = true;
		_nameGetterWorker.Join();
	}
			
}

