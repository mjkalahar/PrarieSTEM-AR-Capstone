using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/**
* Basic script for Timer Slider that updates the input field when 
* slider is changed
*/
public class Timer : MonoBehaviour
{
    InputField textComponent;
    /**
    * Start is called before the first frame update
    * Get input field object
    */
    void Start()
    {
        textComponent = GetComponent<InputField>();
    }

    /**
    * Updates the input field with float value from param, automatically assigned dynamic floats from inspector in slider
    * @param sliderValue Float value of current time limit from slider
    */
    public void SetValueFromSlider(float sliderValue)
    {
        if(sliderValue != null && textComponent != null)
            textComponent.text = sliderValue.ToString() + ":00";
    }
}
