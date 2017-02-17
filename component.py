import thread
import time

import network

ip_elevator = ["129.241.187.153", "129.241.187.155", "129.241.187.151"]
my_ip = network.Get_IP_Address()
connection = []
address = []

#---------------------------------------------------------------------------------------------------------
def Listen_To_Components():
	print "I am listening for connections from components!"

	s = network.Bind_Socket(my_ip, 22290)

	while True:
		s.listen(1)

		(conn, addr) = network.Accept_Connection(s)

		connection.append(conn)		
		address.append(addr[0])

		print "I am connected to ", len(connection), " components!" 
		print "New Connected address:", address[-1]

#---------------------------------------------------------------------------------------------------------
def Connect_To_Components():
	print "I am trying to connect to components!"

	while True:
		for ip in ip_elevator:
			if (ip > my_ip) and (ip not in address): 
				try:
					connection.append( network.Create_Socket(ip, 22290) )
					address.append(ip)
					print "New Connected address:", address[-1]
					print "I am connected to ", len(connection), " components!" 
				except:	
					print "I did not manage to connect to ", ip
			time.sleep(1)

#---------------------------------------------------------------------------------------------------------
#def Watchdog_Client_Alive(conn, addr):

#def Main_Thread(conn, addr):

#add process pair
#---------------------------------------------------------------------------------------------------------
print 'I am ', my_ip

thread.start_new_thread(Listen_To_Components,())
thread.start_new_thread(Connect_To_Components,())

while True:
	time.sleep(1)

