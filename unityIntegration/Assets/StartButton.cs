using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;	

public class StartButton : MonoBehaviour
{
	Button button;
    // Start is called before the first frame update
    void Start()
    {
        button =  GetComponent<Button>();
    }

    // Update is called once per frame
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
