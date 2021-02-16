using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using NetMQ.Sockets;
using NetMQ;
using System.Threading;
using Newtonsoft.Json.Linq;

public class DropDownMenu : MonoBehaviour
{
	private int _listeningPort = 5051;
    private string _serverIP = "tcp://ec2-13-58-201-148.us-east-2.compute.amazonaws.com:";
	//Options is the list of strings that is shown to the user
	List<string> options = new List<string>{"Searching, please wait"};
	List<int> ports = new List<int>{};
	private static string _json = "[]";
	
	//Menu is the "game component"
	Dropdown menu;
	//Pi's port number
	public static int port = -1;

	private PiNameGetter _piNameGetter;

    // Start is called before the first frame update
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
		_piNameGetter = new PiNameGetter(UpdateList, _serverIP + _listeningPort);
		_piNameGetter.Start();
    }

    // Update is called once per frame
    void Update()
    {
		int v = menu.value;
		JArray arr = JArray.Parse(_json);
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
	
	void OnDestroy()
	{
		_piNameGetter.Stop();
	}
	
	void menuChange(Dropdown change){
		port = ports[change.value];
	}
	
	//This is the message delegate that the 
	// listening thread will use to update the list
	void UpdateList(string message)
	{
		_json = message;

	}

}


public class PiNameGetter
{
	private readonly Thread _nameGetterWorker;
	private bool _nameGetterCancelled;
	
	public delegate void MessageDelegate(string message);
	private readonly MessageDelegate _messageDelegate;
	
	private string _serverIP;
	private string _newJsonString = "";
	private string _jsonString = "";
	
	public PiNameGetter(MessageDelegate messageDelegate, string serverIPin)
	{
		_serverIP = serverIPin;
		
		_messageDelegate = messageDelegate;
		_nameGetterWorker = new Thread(nameGetterWork);
	}
	public void Start()
	{
		_nameGetterCancelled = false;
		_nameGetterWorker.Start();
	}
	
	private void nameGetterWork()
	{
		AsyncIO.ForceDotNet.Force();
		using (var subSocket = new SubscriberSocket())
		{
			subSocket.Options.ReceiveHighWatermark = 1;
			subSocket.Connect(_serverIP);
			subSocket.Subscribe("");
			
			while (!_nameGetterCancelled)
			{

				if (!subSocket.TryReceiveFrameString(out _newJsonString)) continue;
				
				if (!_newJsonString.Equals(_jsonString))
				{
					_jsonString = _newJsonString;
					_messageDelegate(_jsonString);
				}
			}
			subSocket.Close();
		}
		NetMQConfig.Cleanup();
	}

	public void Stop()
	{
		_nameGetterCancelled = true;
		_nameGetterWorker.Join();
	}
			
}

