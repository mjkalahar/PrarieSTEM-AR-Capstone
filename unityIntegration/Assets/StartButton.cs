using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;	

/**
* Basic script for StartButton on main menu that switches if it is interactable based on value selected
*/
public class StartButton : MonoBehaviour
{
	Button button;
    /**
    * Start is called before the first frame update
    * Get button object
    */
    void Start()
    {
        button =  GetComponent<Button>();
    }

    /**
    * Update is called once per frame
    * Check drop down port value and set button interactable accordingly
    */
    void Update()
    {
        if (DropDownMenu.port == -1)
		{
			button.interactable = false;
		}
		else
		{
			button.interactable = true;
		}
    }
}
