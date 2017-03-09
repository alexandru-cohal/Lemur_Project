import socket

#----------------------------------------------------------------------------------
def Create_Socket(ip, port):
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((ip, port))

	return conn

#----------------------------------------------------------------------------------
def Bind_Socket(ip, port):
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.bind((ip, port))

	return conn

#----------------------------------------------------------------------------------
def Get_IP_Address():
	# Source: http://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))

	return s.getsockname()[0]

#----------------------------------------------------------------------------------
def Accept_Connection(s):
	(conn, addr) = s.accept()

	return (conn, addr)
		
#----------------------------------------------------------------------------------
def Receive_Message(conn):
	return conn.recv(100)

#----------------------------------------------------------------------------------
def Send_Message(conn, message):
	conn.send(message)

#----------------------------------------------------------------------------------	
def Broadcast_Message(connection, message):
	# Limited Broadcast - only to the connections in the list
	for conn in connection:
		Send_Message(conn, message)

#----------------------------------------------------------------------------------
def Close_Connection(conn):
	conn.close()
