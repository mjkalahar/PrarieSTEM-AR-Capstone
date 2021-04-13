using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Timer : MonoBehaviour
{
    InputField textComponent;
    // Start is called before the first frame update
    void Start()
    {
        textComponent = GetComponent<InputField>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void SetValueFromSlider(float sliderValue)
    {
        if(sliderValue != null && textComponent != null)
            textComponent.text = sliderValue.ToString() + ":00";
    }
}
