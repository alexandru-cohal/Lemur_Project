import thread
import socket
import time

connection = []
address = []

def Accept_Connections():
	print "I am inside the Accept_Connections Thread!"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("129.241.187.57", 20023))

	while True:
		s.listen(1)

		(conn, add) = s.accept()
		connection.append(conn)		
		address.append(add)

		print "I am connected to ", len(connection), " clients!" 
		print "New Connected address:", address[-1]

		thread.start_new_thread(Connection,(conn, add))


def Connection(conn, add):
	print "I am in the thread of the connection to address ", add

	while True:
		data = conn.recv(100)

		if not data:
			print "Client ", add, "died :("

			connection.pop(address.index(add))
			address.pop(address.index(add))

			print "I am connected to ", len(connection), " clients!" 

			break
		print "Data received from ", add, ": ", data

	conn.close()


thread.start_new_thread(Accept_Connections,())
time.sleep(100)
