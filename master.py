import threading
import socket
import time
import smbus
import string
import RPi.GPIO as GPIO
import os
from random import randint

## Disable warning as they get a bit annoying
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

## Set a random port so it can restart incase the script crashes
RPort = randint(6000,8000)

## Define all pins used
LEDPIN = 8    ## LED headlights
BUZPIN = 7    ## Horn
MOTEN = 18    ## Motor enable pin
MOTA = 23     ## Motor A pin
MOTB = 24     ## Motor B pin

GPIO.setup(BUZPIN, GPIO.OUT)
GPIO.setup(LEDPIN, GPIO.OUT)
GPIO.setup(MOTEN, GPIO.OUT)
GPIO.setup(MOTA, GPIO.OUT)
GPIO.setup(MOTB, GPIO.OUT)

class ReadNunchuck(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		

	def run(self):
		bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		bot.bind(('', int(RPort)))
		bot.listen(5)
		client, address = bot.accept()
		client2, address = bot.accept()
		client3, address = bot.accept()
		client4, address = bot.accept()

		total = 0
		while True:
			bus = smbus.SMBus(1)
			bus.write_byte_data(0x52, 0xF0, 0x55)

			while True:
				
				buf = bus.read_i2c_block_data(0x52, 0x00, 6)
			
			        data = [0x00]*6

			        for i in range(len(buf)):

			            data[i] = buf[i]

				string = "%03d" %(data[0])
				string = string + ",%03d" %(data[1])

				string = string + ",%d" % (data[5] & 0x01) #Btn Z
				string = string + ",%d" % (data[5] & 0x02) #Btn C

				client.send(string)
				client2.send(string)
				client3.send(string)
				client4.send(string)

class Buzzer(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)

        def run(self):
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect(("127.0.0.1", RPort))
		print "Connected Buzzer"
		GPIO.output(BUZPIN, GPIO.LOW)
                while True:
			buffer = client.recv(11)
			data = [0x00]*4
			data = string.split(buffer,",")
			if data[2] == "0":
				GPIO.output(BUZPIN, GPIO.HIGH)
	                        time.sleep(0.0003)
	                        GPIO.output(BUZPIN, GPIO.LOW)
	                        time.sleep(0.0003)
				


class Lights(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)

        def run(self):
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(("127.0.0.1", RPort))
                print "Connected Lights"
		storedState = 0
		changeState = 0
                GPIO.output(LEDPIN, GPIO.LOW)
                while True:
                        buffer = client.recv(11)
                        data = [0x00]*4
                        data = string.split(buffer,",")
			if data[3] == "0":
                		if changeState == 1:
					if storedState == 1:
						storedState = 0
						GPIO.output(LEDPIN, GPIO.HIGH)
					else:
						storedState = 1
						GPIO.output(LEDPIN, GPIO.LOW)
				changeState = 0		
			else:
				changeState = 1


class Motor(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)



        def run(self):

		def setspeed(v):
	               
	                voff = 100 - v
	               
                        GPIO.output(MOTEN, GPIO.HIGH)
                        time.sleep(v/10000.0)
                        GPIO.output(MOTEN, GPIO.LOW)
                        time.sleep(voff/10000.0)
                        


                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(("127.0.0.1", RPort))
                print "Connected Motor"
                GPIO.output(MOTEN, GPIO.LOW)
		GPIO.output(MOTA, GPIO.LOW)
		GPIO.output(MOTB, GPIO.LOW)
		count = 0
                while True:
                        buffer = client.recv(11)
                        data = [0x00]*4
                        data = string.split(buffer,",")
			data[1] = float(data[1])
			
			if data[1] < 120:
				GPIO.output(MOTA, GPIO.HIGH)
		                GPIO.output(MOTB, GPIO.LOW)
				speed = 100 - (( data[1] / 120 ) * 100 )
				if count == 4:
					setspeed(speed)
					count = 0
				else:
					count = count + 1

			elif data[1] > 135:
				GPIO.output(MOTA, GPIO.LOW)
                                GPIO.output(MOTB, GPIO.HIGH)
                                speed = 100 - ((( 255 - data[1]) / 120 ) * 100 )
                                if count == 4:
                                        setspeed(speed)
                                        count = 0
                                else:
                                        count = count + 1

			else:
				GPIO.output(MOTEN, GPIO.LOW)
        		        GPIO.output(MOTA, GPIO.LOW)
	                	GPIO.output(MOTB, GPIO.LOW)


class Steering(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)

	def run(self):
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(("127.0.0.1", RPort))
                print "Connected Steering"
                count = 0
		anglestring = ""
                while True:
                        buffer = client.recv(11)
                        data = [0x00]*4
                        data = string.split(buffer,",")
                        data[0] = float(data[0])
			if count == 20:
                        	angle = ((data[0] / 255) * 100 ) + 40
				anglestring = "echo 0=%d > /dev/servoblaster" % angle
				os.system(anglestring)
                                count = 0
                        else:
                        	count = count + 1
			
		

thread1 = ReadNunchuck()
thread2 = Buzzer()
thread3 = Lights()
thread4 = Motor()
thread5 = Steering()
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
