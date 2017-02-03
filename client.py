import socket
import time

import network

conn = network.Create_Socket("129.241.187.153", 20021)

while True:
	data = network.Receive_Message(conn)
	
	print "Received from Server: ", data

	if data == "[Lemur] AYA?":
		network.Send_Message(conn, "[Lemur] IAA")

network.Close_Connection(conn)
