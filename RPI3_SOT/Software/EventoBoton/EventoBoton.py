#!/usr/bin/env python2

#Configuration Files
import ConfigParser
settings= ConfigParser.ConfigParser()
settings.read("/home/pi/.EventoBoton.cfg")
CMData = ConfigParser.ConfigParser()
CMData.read("/home/pi/.CorreoCM.cfg")
#Debug Params
debug=1

#Email Params

mail_user = settings.get("CorreoClienteGmail", "user")
mail_pass = settings.get("CorreoClienteGmail", "pass")
to = CMData.get('CorreoComunityManager','email')
subject = 'SelfieOverTable'
img = '/home/pi/Pictures/image.jpg'

#Function as a Service imports and defs
import logging
import logging.handlers
import sys
# Deafults
LOG_FILENAME = "/tmp/EventoBoton.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)
# Make a class we can use to capture stdout and sterr in the log
class Logger_Service(object):
	def __init__(self, logger, level):
		"""Needs a logger and a logger level."""
		self.logger = logger
		self.level = level

	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = Logger_Service(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = Logger_Service(logger, logging.ERROR)

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
first=0

#Modulo correos (gmail)
import yagmail


#Modulo Camera
import picamera
camera = picamera.PiCamera()
camera.resolution = (1440,1080)
camera.hflip = True
camera.vflip = True
camera.iso=800
time.sleep(2)
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode='off'
time.sleep(1)



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
		#print "RF class initialized"
		logger.info("RF class initialized")
	rf.rcCalibration()
	if(debug==1):
		#print "RF Calibrated"
		logger.info("RF Calibrated")
	if(debug==1):
		#print "RF Registry Override"
		logger.info("RF Registry Override")
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
		#print "Shutting down"
		logger.info("Shutting down")
	rf.shutdown()

#Funciones Neopixels
def pixels_color(strip,color):
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
	strip.show()
	
def BlinkEffect(strip, color, duration):
	pixels_color(strip,color)
	time.sleep(duration)
	pixels_color(strip,Color(0, 0, 0))

def TimerEffect(strip, start_time, wait_for, color, color_finish):
	elapsed_time = time.time() - start_time
	ratio=elapsed_time/wait_for
	n=strip.numPixels()
	x=n*ratio
	if(ratio<1):
		for i in range(int(x)):
			strip.setPixelColor(i, color_finish)
		for i in range(int(n-x+1)):
			strip.setPixelColor(i+int(x), color)
		strip.show()
	else:
		global first
		if (first==1):
			pixels_color(strip,Color(0,0,0))
			time.sleep(0.4)
			pixels_color(strip,color_finish)
			time.sleep(0.4)
			pixels_color(strip,Color(0,0,0))
			time.sleep(0.4)
			pixels_color(strip,color_finish)
			time.sleep(0.4)
			pixels_color(strip,Color(0,0,0))
			first=0
		
def TimerEffect2(strip, start_time, wait_for, color, color_finish):
	elapsed_time = time.time() - start_time
	ratio=elapsed_time/wait_for
	n=strip.numPixels()
	x=n*ratio
	if(ratio<1):
		for i in range(int(x)+1):
			strip.setPixelColor(i, color_finish)
		for i in range(int(n-x+2)):
			strip.setPixelColor(i+int(x), color)
		strip.show()
	else:
		pixels_color(strip,color_finish)

def TakePictureEffect(strip):
	#pixels_color(strip,Color(0, 0, 0))
	#time.sleep(0.2)
	#pixels_color(strip,Color(100, 100, 100))
	#time.sleep(0.5)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.3)
	pixels_color(strip,Color(100, 100, 100))
	time.sleep(0.5)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.3)
	pixels_color(strip,Color(100, 100, 100))
	time.sleep(0.5)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.3)
	pixels_color(strip,Color(255, 255, 255))
	time.sleep(0.2)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.15)
	pixels_color(strip,Color(255, 255, 255))
	time.sleep(0.15)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.15)
	pixels_color(strip,Color(255, 255, 255))
	time.sleep(0.10)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.10)
	pixels_color(strip,Color(255, 255, 255))
	time.sleep(0.10)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.10)
	pixels_color(strip,Color(255, 255, 255))
	time.sleep(0.10)
	pixels_color(strip,Color(0, 0, 0))
	time.sleep(0.08)
	pixels_color(strip,Color(255, 255, 255))
	time.sleep(0.08)
	pixels_color(strip,Color(0, 0, 0))
	#Capture Picture on Pictures Folder
	time.sleep(0.1)
	camera.capture('/home/pi/Pictures/image.jpg')	
	time.sleep(0.1)
	#White stop
	pixels_color(led_strip,Color(255, 255, 255))
	time.sleep(0.6) #Delay	
			
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
		#print "Receiving Packets\n"
		logger.info("Receiving Packets\n")
	if(debug==1):
		#print "Waiting\n"
		logger.info("Waiting\n")
		
	#Receive Packets from RFM69 (Remote Button)	
	
	#Wait for interrupt initialization
	#time.sleep(2)
	
	
	first=0
	#Capture to init the camera
	camera.capture('/home/pi/Pictures/image.jpg')
	#Ready Indication
	BlinkEffect(led_strip,Color(0,0,255),0.5)
	#start_time=time.time()
	rf.receiveBegin()
	while True:
		#Non blocking receive sequence
		if rf.receiveDone():
			if (first==0):
				#Print Packet Received
				#print "%s from %s RSSI:%s" % ("".join([chr(letter) for letter in rf.DATA]), rf.SENDERID, rf.RSSI)
				logger.info("".join([chr(letter) for letter in rf.DATA]))
				#"Count down" Animation
				start_time=time.time()
				while((time.time()-start_time)<0.6):
					TimerEffect2(led_strip,start_time, 0.5, Color(0, 0, 0), Color(255, 255, 0))
				#theaterChase(led_strip, Color(255, 255, 255),18,8)  # White theater chase
				TakePictureEffect(led_strip)
				#LEDs off
				pixels_color(led_strip,Color(0, 0, 0))
				#Capture Picture on Pictures Folder
				#camera.capture('/home/pi/Pictures/image.jpg')
				#Green, wait to send email
				pixels_color(led_strip,Color(20, 00, 0))
				#Prepare Email Info
				t = datetime.datetime.now()
				body = "Mesa: XYZ \n" + t.strftime("%Y-%m-%d %H:%M:%S")
				#Send Email with picture
				yag = yagmail.SMTP(mail_user , mail_pass)
				yag.send(to = to, subject = subject, contents = [body, img])
				#LEDs off
				pixels_color(led_strip,Color(0, 0, 0))
				first=1
				#Wait for another button trigger
				rf.receiveBegin()
				start_time=time.time()
			rf.receiveBegin()
		else: #Wait for next time avaliable 
			time.sleep(.1)
			if(first==1): #No effect on startup
				TimerEffect(led_strip,start_time, 10, Color(100, 0, 0), Color(255, 255, 0))
		#Kill signal evaluation
		if killer.kill_now:
		  break
	#Shutdown RFM69	
	ShutdownRF()
	if(debug==1):
		#print "End of the program"
		logger.info("End of the program")
