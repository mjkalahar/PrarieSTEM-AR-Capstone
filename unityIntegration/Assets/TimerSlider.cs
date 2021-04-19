using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class TimerSlider : MonoBehaviour
{
    Slider timerSlider;
    float value = 1;
    // Start is called before the first frame update
    void Start()
    {
        timerSlider = GetComponent<Slider>();
        
    }

    void OnEnable()
    {
        if(timerSlider != null)
            value = timerSlider.value;
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void Reset()
    {
        timerSlider.value = value;
    }

}
