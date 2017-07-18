#!/usr/bin/env python2

#Bibliotecas RFM69
import RFM69
from RFM69registers import *
import RPi.GPIO as GPIO

#Biblioteca Neopixels
from neopixel import *

#Bibliotecas Tiempo y flujo de programa
import datetime
import time
import signal #Kill Signal

#Debug Params
debug=1

#Parametros Neopixels
# LED Ring configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 100     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

#Funciones RF

def InitRF():
	global rf
	rf = RFM69.RFM69(RF69_915MHZ, 3, 1, True)
	if(debug==1):
		print "RF class initialized"
	rf.rcCalibration()
	if(debug==1):
		print "RF Calibrated"
	if(debug==1):
		print "RF Registry Override"
	rf.writeReg(0x03, 0x00)
	rf.writeReg(0x04, 0x80)
	rf.writeReg(0x05, 0x10)
	rf.writeReg(0x06, 0x00)
	rf.writeReg(0x0A, 0x41)
	rf.writeReg(0x0D, 0x92)
	rf.writeReg(0x0E, 0xF5)
	rf.writeReg(0x0F, 0x20)
	rf.writeReg(0x11, 0x7F)
	rf.writeReg(0x12, 0x09)
	rf.writeReg(0x13, 0x1A)
	rf.writeReg(0x18, 0x08)
	rf.writeReg(0x19, 0xE0)
	rf.writeReg(0x1A, 0xE0)
	rf.writeReg(0x25, 0x00)
	rf.writeReg(0x26, 0x05)
	rf.writeReg(0x2E, 0x88)
	rf.writeReg(0x2F, 0x2D)
	rf.writeReg(0x30, 0xD4)
	rf.writeReg(0x31, 0x00)
	rf.writeReg(0x32, 0x00)
	rf.writeReg(0x33, 0x00)
	rf.writeReg(0x34, 0x00)
	rf.writeReg(0x35, 0x00)
	rf.writeReg(0x36, 0x00)
	rf.writeReg(0x37, 0xD0)
	rf.writeReg(0x38, 0x40)
	rf.writeReg(0x39, 0x00)
	rf.writeReg(0x3D, 0x03)
	rf.writeReg(0x3E, 0x31)
	rf.writeReg(0x3F, 0x32)
	rf.writeReg(0x40, 0x33)
	rf.writeReg(0x41, 0x34)
	rf.writeReg(0x42, 0x35)
	rf.writeReg(0x43, 0x36)
	rf.writeReg(0x44, 0x37)
	rf.writeReg(0x45, 0x38)
	rf.writeReg(0x46, 0x31)
	rf.writeReg(0x47, 0x32)
	rf.writeReg(0x48, 0x33)
	rf.writeReg(0x49, 0x34)
	rf.writeReg(0x4A, 0x35)
	rf.writeReg(0x4B, 0x36)
	rf.writeReg(0x4C, 0x37)
	rf.writeReg(0x4D, 0x38)
	
def ShutdownRF():
	if(debug==1):
		print "Shutting down"
	rf.shutdown()

#Funciones Neopixels
	
def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)
				
def pixels_color(strip,color):
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
	strip.show()
	
		
class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

if __name__ == '__main__':
	#Kill Signal Handler
	killer = GracefulKiller()
	
	# Create NeoPixel object
	led_strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize Neopixel
	led_strip.begin()
	pixels_color(led_strip,Color(0, 0, 0))
	#Initialize RFM69
	InitRF()
	if(debug==1):
		print "Receiving Packets\n"
	if(debug==1):
		print "Waiting\n"
		
	#Receive Packets from RFM69 (Remote Button)	
	rf.receiveBegin()
	while True:
		#Non blocking receive sequence
		if rf.receiveDone():
			#Print Packet Receives
			print "%s from %s RSSI:%s" % ("".join([chr(letter) for letter in rf.DATA]), rf.SENDERID, rf.RSSI)
			theaterChase(led_strip, Color(255, 255, 255),18,8)  # White theater chase
			pixels_color(led_strip,Color(0, 0, 0))
			rf.receiveBegin()
		else:
			time.sleep(.1)
		#Kill signal evaluation
		if killer.kill_now:
		  break
	#Shutdown RFM69	
	ShutdownRF()
	if(debug==1):
		print "End of the program"
