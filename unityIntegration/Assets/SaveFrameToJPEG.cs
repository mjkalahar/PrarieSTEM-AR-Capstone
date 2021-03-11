using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Collections.Concurrent;
using System.Threading;
using NetMQ;
using NetMQ.Sockets;

public class SaveFrameToJPEG : MonoBehaviour
{
    private int port;
    private int offset = 10000;
    private string serverIP = "tcp://ec2-34-201-129-143.compute-1.amazonaws.com:";
    Texture2D camTexture;
    

    // This is an object that spins up a thread to manage the socket connection
    //and then hands off the data to a "messageDelegate" that handles the data
    //in this instance the "messageDelegate" is the HandleMessage function
    private NetMqListener _netMqListener;

    // This function handles the message
    // This is where we should put logic to display the image
    private void HandleMessage(byte[] message)
    {
        this.camTexture.LoadImage(message);
        byte[] jpeg = ImageConversion.EncodeToJPG(this.camTexture);
        var dirPath = Application.dataPath + "/PiImages/";
        if (!Directory.Exists(dirPath))
        {
            Directory.CreateDirectory(dirPath);
        }
        File.WriteAllBytes(dirPath + "Image" + ".jpeg", jpeg);
        Canvas.ForceUpdateCanvases();
    }

    // Start is called before the first frame update
    void Start()
    {
        port = 10000;
        this.camTexture = new Texture2D(2, 2);
        // Create and start listener object
        _netMqListener = new NetMqListener(HandleMessage, serverIP + (port + offset));
        UnityEngine.Debug.Log(serverIP + (port + offset));
        _netMqListener.Start();
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
