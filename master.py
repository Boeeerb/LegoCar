import threading
import socket
import time
import smbus

class ReadNunchuck(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		

	def run(self):
		bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		bot.bind(('', int(6000)))
		bot.listen(5)
		client, address = bot.accept()
		print "Connection from something"
		total = 0
		while True:
			bus = smbus.SMBus(1)
			bus.write_byte_data(0x52, 0xF0, 0x55)

			while True:
				time.sleep(0.2)
				buf = bus.read_i2c_block_data(0x52, 0x00, 6)
				print buf
			
			        data = [0x00]*6

			        for i in range(len(buf)):

			            data[i] = buf[i]

				string = "%d" %(data[0])
				string = string + ",%d" %(data[1])

				client.send(string)

class Buzzer(threading.Thread):
        def __init__(self):
                threading.Thread.__init__(self)

        def run(self):
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect(("127.0.0.1", 6000))
		print "Connected to Read"
		total = 0
                while True:
			buffer = client.recv(10)
			print buffer
			time.sleep(0.2)


thread1 = ReadNunchuck()
thread2 = Buzzer()
thread1.start()
thread2.start()

