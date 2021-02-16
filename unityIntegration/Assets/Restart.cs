using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Restart : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        Application.LoadLevel (Application.loadedLevel);	
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
