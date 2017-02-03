import thread
import socket
import time

import network

connection = []
address = []
flag_client_alive = []

#-------------------------------------------------------
def Connect_To_Clients():
	print "I am listening for connections!"

	s = network.Bind_Socket("129.241.187.153", 20021)

	while True:
		s.listen(1)

		(conn, addr) = network.Accept_Connection(s)

		connection.append(conn)		
		address.append(addr[0])
		flag_client_alive.append(0)

		print "I am connected to ", len(connection), " clients!" 
		print "New Connected address:", address[-1]

		thread.start_new_thread(Watchdog_Client_Alive, (conn, addr[0]))
		thread.start_new_thread(Main_Thread, (conn, addr[0])) ## Change the name

#----------------------------------------------------------------------------------
def Watchdog_Client_Alive(conn, addr):
	while True:
		try:
			network.Send_Message(conn, "[Lemur] AYA?")
		except:
			print "Client ", addr, " is dead! (Software crash 2)" 
			break

		time.sleep(2)

		client_index = address.index(addr) 
		if flag_client_alive[client_index] == 1:
			print "Client ", addr, " is alive!"
		else:
			print "Client ", addr, " is dead! (Losing Network or Software crash)"

			connection.pop(client_index)
			address.pop(client_index)
			flag_client_alive.pop(client_index)

			print "I am now connected to ", len(connection), " clients!" 				
			break

		flag_client_alive[client_index] = 0

#----------------------------------------------------------------------------------
def Main_Thread(conn, addr):
	global flag_client_alive
	
	while True:
		data = network.Receive_Message(conn)

		client_index = address.index(addr)

		if not data:
			print "Client ", addr, "is dead! (Software crash)"

			flag_client_alive[client_index] = 0

			break

		elif data == "[Lemur] IAA":
			flag_client_alive[client_index] = 1
			#print addr[0], "said IAA"

		else:
			print "Data received from ", addr, ": ", data

	network.Close_Connection(conn)
#----------------------------------------------------------------------------------
thread.start_new_thread(Connect_To_Clients,())
time.sleep(100)
