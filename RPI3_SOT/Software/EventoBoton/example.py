#!/usr/bin/env python2

import RFM69
from RFM69registers import *
import datetime
import time
import RPi.GPIO as GPIO

test = RFM69.RFM69(RF69_915MHZ, 3, 1, True)
print "class initialized"
print "reading all registers"
results = test.readAllRegs()
for result in results:
	print result
print "Performing rcCalibration"
test.rcCalibration()
print "setting high power"
test.setHighPower(True)
print "Checking temperature"
print test.readTemperature(0)
print "setting encryption"
#test.encrypt("1234567891011121")
test.encrypt("1234567812345678")
#test.encrypt("\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08")
#print "sending blah to 2"
#if test.sendWithRetry(2, "blah", 3, 20):
#    print "ack recieved"
print "reading"
while True:
	test.writeReg(0x00, 0x1A)
	test.writeReg(0x01, 0x04)
	test.writeReg(0x02, 0x01)
	test.writeReg(0x03, 0x00)
	test.writeReg(0x04, 0x80)
	test.writeReg(0x05, 0x10)
	test.writeReg(0x06, 0x00)
	test.writeReg(0x0A, 0x41)
	test.writeReg(0x0D, 0x92)
	test.writeReg(0x0E, 0xF5)
	test.writeReg(0x0F, 0x20)
	test.writeReg(0x11, 0x7F)
	test.writeReg(0x12, 0x09)
	test.writeReg(0x13, 0x1A)
	test.writeReg(0x18, 0x08)
	test.writeReg(0x19, 0xE0)
	test.writeReg(0x1A, 0xE0)
	test.writeReg(0x25, 0x00)
	test.writeReg(0x26, 0x05)
	test.writeReg(0x2E, 0x88)
	test.writeReg(0x2F, 0x2D)
	test.writeReg(0x30, 0xD4)
	test.writeReg(0x31, 0x00)
	test.writeReg(0x32, 0x00)
	test.writeReg(0x33, 0x00)
	test.writeReg(0x34, 0x00)
	test.writeReg(0x35, 0x00)
	test.writeReg(0x36, 0x00)
	test.writeReg(0x37, 0xD0)
	test.writeReg(0x38, 0x40)
	test.writeReg(0x39, 0x00)
	test.writeReg(0x3D, 0x03)
	test.writeReg(0x3E, 0x31)
	test.writeReg(0x3F, 0x32)
	test.writeReg(0x40, 0x33)
	test.writeReg(0x41, 0x34)
	test.writeReg(0x42, 0x35)
	test.writeReg(0x43, 0x36)
	test.writeReg(0x44, 0x37)
	test.writeReg(0x45, 0x38)
	test.writeReg(0x46, 0x31)
	test.writeReg(0x47, 0x32)
	test.writeReg(0x48, 0x33)
	test.writeReg(0x49, 0x34)
	test.writeReg(0x4A, 0x35)
	test.writeReg(0x4B, 0x36)
	test.writeReg(0x4C, 0x37)
	test.writeReg(0x4D, 0x38)
	#results = test.readAllRegs()
	#for result in results:
		#print result
	test.receiveBegin()
	while not test.receiveDone():
		time.sleep(.1)
		#if GPIO.input(18):
		#	print('Input was HIGH')
		#else:
		#	print('Input was LOW')
		
	print "%s from %s RSSI:%s" % ("".join([chr(letter) for letter in test.DATA]), test.SENDERID, test.RSSI)
	if test.ACKRequested():
		test.sendACK()
print "shutting down"
test.shutdown()
