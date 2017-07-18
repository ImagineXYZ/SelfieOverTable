// Remote Button
// Imagine XYZ
// Project: Selfie Over Table
// Hardware: FeatherM0 RFM69 + Neopixels + Push Button
// Bryan Salazar R

#include "Arduino.h"

//Neopixels Library with Effects
//https://github.com/kitesurfer1404/WS2812FX
#include <WS2812FX.h>

//Button pin and variables
int Button_PIN = 5;
int button;

//Neopixels Definitions
#define LED_COUNT 3 //Number of neopixels
#define LED_PIN 6 //Neopixels data pin

//Neopixels variables
WS2812FX leds = WS2812FX(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ400);
int leds_state = 0; //Actual State, initial state 0

//Time variables
unsigned long now = 0;

void setup(){
	//Initialize BUtton
	pinMode(Button_PIN,INPUT);

	//Initialize Neopixels
	//Pin mode inside init()
	leds.init();
	leds.setBrightness(100);
	leds.setSpeed(400);
	leds.setMode(FX_MODE_RAINBOW);
	leds.start();

}


void loop(){
	//Time tracking
	now = millis();

	//Neopixels loop service
	leds.service();

	//Button logic
	button=digitalRead(Button_PIN);
	if(button==1){
		delay(50); //Anti-bounce
		if(button==1){ //Button Pressed
			Button_Pressed();
			Button_wait_relase();
		}
	}
}

void Button_Pressed(){
	//Neopixels state machine
	switch (leds_state){
	case 0:
		//Start Neopixels Sequence
		leds.start();
		leds_state=1;
		break;
	case 1:
		//Stop Neopixels Sequence
		leds.stop();
		leds_state=0;
		break;
	default:
		break;
	}

}

void Button_wait_relase(){
	while(button==1){
		button=digitalRead(Button_PIN);
	}
}
