import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("129.241.187.57", 20023))

while True:
	data = s.recv(100)
	
	print "Received from Server: ", data

	if data == "[Lemur] AYA?":
		s.send("[Lemur] IAA")

s.close()
