import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("129.241.187.57", 20023))

while True:
	s.send("[Lemur] AYA?")
	time.sleep(3)

s.close()

