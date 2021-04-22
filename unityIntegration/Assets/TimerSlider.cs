using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/**
* Basic script for Timer Slider saves value between saving/canceling/main menu
*/
public class TimerSlider : MonoBehaviour
{
    Slider timerSlider;
    float value = 1;
    /**
    * Start is called before the first frame update
    * Get Slider object
    */
    void Start()
    {
        timerSlider = GetComponent<Slider>();
    }

    /**
    * OnEnable is called when object is enabled in scene
    * If slider is set to a value, store the value
    */
    void OnEnable()
    {
        if(timerSlider != null)
            value = timerSlider.value;
    }

    /**
    * Reset the value, is called by the exit button in the settings screen
    * Resets the slider to the last stored value
    */
    public void Reset()
    {
        timerSlider.value = value;
    }

}
