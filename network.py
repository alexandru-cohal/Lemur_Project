#import thread
import socket

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
def Broadcast_Message(message):
	print "Bbb"
	## To be implemented

#----------------------------------------------------------------------------------
def Close_Connection(conn):
	conn.close()
