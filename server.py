import threading
import thread
import socket
import time

connection = []
address = []
flag_client_alive = []

client_index_lock = threading.Lock()

#----------------------------------------------------------------------------------
def Accept_Connections():
	print "I am inside the Accept_Connections Thread!"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("129.241.187.153", 20021))

	while True:
		s.listen(1)

		(conn, addr) = s.accept()
		connection.append(conn)		
		address.append(addr[0])
		flag_client_alive.append(0)

		print "I am connected to ", len(connection), " clients!" 
		print "New Connected address:", address[-1]

		thread.start_new_thread(Receive_Messages_From_Single_Client, (conn, addr[0]))
		thread.start_new_thread(Watchdog_Client_Alive, (conn, addr[0]))

#----------------------------------------------------------------------------------
def Watchdog_Client_Alive(conn, addr):
	while True:
		try:
			conn.send("[Lemur] AYA?")
		except:
			print "Client ", addr, " is dead! (Software crash 2)" 
			break

		time.sleep(2)

		client_index_lock.acquire()
		client_index = address.index(addr) 
		if flag_client_alive[client_index] == 1:
			print "Client ", addr, " is alive!"
			flag_client_alive[client_index] = 0

			client_index_lock.release()
		else:
			print "Client ", addr, " is dead! (Losing Network or Software crash)"
			connection.pop(client_index)
			address.pop(client_index)
			flag_client_alive.pop(client_index)
			print "I am now connected to ", len(connection), " clients!" 			
			client_index_lock.release()	
			break

		#flag_client_alive[client_index] = 0


#----------------------------------------------------------------------------------
def Receive_Messages_From_Single_Client(conn, addr):
	global flag_client_alive

	while True:
		data = conn.recv(100)

		client_index_lock.acquire()
		client_index = address.index(addr)

		if not data:
			print "Client ", addr, "is dead! (Software crash)"

			flag_client_alive[client_index] = 0
			client_index_lock.release()

			break

		elif data == "[Lemur] IAA":
			flag_client_alive[client_index] = 1
			#print addr[0], "said IAA"

		else:
			print "Data received from ", addr, ": ", data

		client_index_lock.release()

	conn.close()

#----------------------------------------------------------------------------------
thread.start_new_thread(Accept_Connections,())
time.sleep(100)
