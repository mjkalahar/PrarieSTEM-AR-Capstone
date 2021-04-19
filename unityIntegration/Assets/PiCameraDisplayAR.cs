using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Threading;
using NetMQ;
using System.IO;
using UnityEngine;
using NetMQ.Sockets;
using System.Diagnostics;
using UnityEngine.UI;

public class PiCameraDisplayAR : MonoBehaviour
{
    // The hardcoded (for now) pi IP and port
    private int port;
    private int offset = 10000;
    private string serverIP = "tcp://ec2-54-164-70-144.compute-1.amazonaws.com:";
    public Text FPSText;
    private int LIMIT = 1000;
    public Text AvgFPS;
    private float lastTime;
    private List<float> FPSList;
    private float startTime;
    float timeLimit;

    Texture2D camTexture;

    RawImage screenDisplay;
    public GameObject arToolkit;
    public GameObject sceneRoot;
    public GameObject gasSlider;
    public GameObject timerSlider;
    public GameObject restart;

    Canvas canvas;

    // This is an object that spins up a thread to manage the socket connection
    //and then hands off the data to a "messageDelegate" that handles the data
    //in this instance the "messageDelegate" is the HandleMessage function
    private NetMqListener _netMqListener;

    // Script Start
    private void Start()
    {
        lastTime = Time.unscaledTime;
        startTime = Time.unscaledTime;
        port = DropDownMenu.port;
        UnityEngine.Debug.Log(port);

        FPSList = new List<float>();

        //initialize cam texture and get the raw image
        this.camTexture = new Texture2D(2, 2);
        this.screenDisplay = GetComponent<RawImage>();
        this.canvas = GetComponent<Canvas>();


        // Create and start listener object
        _netMqListener = new NetMqListener(HandleMessage, serverIP + (port + offset));
        _netMqListener.Start();
        arToolkit.GetComponent<ARController>().StartAR();
        sceneRoot.GetComponent<AROrigin>().enabled = true;


        float timerSliderValue = timerSlider.GetComponent<Slider>().value;
        if (timerSliderValue > 0)
            timeLimit = timerSliderValue * 60;
        else
            timeLimit = 0;
    }

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
        //4screenDisplay.texture = camTexture;

        float diffTime = Time.unscaledTime - lastTime;
        float fps = -1f;
        if (diffTime > 0)
        {
            fps = 1f / diffTime;
            FPSText.text = String.Format("FPS: {0:0.00}", fps);
            lastTime = Time.unscaledTime;

            if (fps >= 0)
            {
                if (FPSList.Count >= LIMIT)
                {
                    FPSList.RemoveAt(0);
                }

                FPSList.Add(fps);

                float total = 0;

                FPSList.ForEach(delegate (float value)
                {
                    total += value;
                });
                float avg = total / FPSList.Count;

                AvgFPS.text = String.Format("Average FPS: {0:0.00}", avg);
            }
        }

        Canvas.ForceUpdateCanvases();
    }

    // When our scripts update function is called, we update the listener
    private void Update()
    {
        _netMqListener.Update();

        if (timeLimit > 0)
        {
            float currentTime = Time.unscaledTime;
            float elapsed = currentTime - startTime;
            gasSlider.GetComponent<Slider>().value = 1 - (elapsed / timeLimit);
            if (elapsed >= timeLimit)
            {
                restart.SetActive(true);
            }
        }
    }

    // Stop the listener on program halt
    private void OnDestroy()
    {
        _netMqListener.Stop();
    }
}