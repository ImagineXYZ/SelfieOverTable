#!/usr/bin/env python2

#Bibliotecas RFM69
import RFM69
from RFM69registers import *
import RPi.GPIO as GPIO

#Bibliotecas Tiempo y flujo de programa
import datetime
import time
import signal #Kill Signal

#Debug Params
debug=1

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
