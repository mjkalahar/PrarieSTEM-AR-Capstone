using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/**
* Class for reloading the application for various reasons
* When X is clicked in top right of screen and when time limit is reached
*/
public class Restart : MonoBehaviour
{
    /**
    * Start is called before the first frame update
    * Load the current loaded level into the application again
    */
    void Start()
    {
        Application.LoadLevel (Application.loadedLevel);	
    }
}
