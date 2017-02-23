import thread
import time

import network

address_elevator = ["129.241.187.152", "129.241.187.155", "129.241.187.151"]
my_address = network.Get_IP_Address()
connection = []
address = []
flag_component_alive = []

#---------------------------------------------------------------------------------------------------------
def Listen_To_Components():
	global connection
	global address

	print "I am listening for connections from components!"

	s = network.Bind_Socket(my_address, 22290)

	while True:
		s.listen(1)

		(conn, addr) = network.Accept_Connection(s)
		addr = addr[0]		

		connection.append(conn)		
		address.append(addr)
		flag_component_alive.append(1)

		print "I am connected to ", len(connection), " components!" 
		print "New Connected address:", address[-1]

		thread.start_new_thread(Receive_From_Component,(conn, addr))
		thread.start_new_thread(Watchdog_Component_Alive,(conn, addr))

#---------------------------------------------------------------------------------------------------------
def Connect_To_Components():
	global connection
	global address_elevator
	global address

	print "I am trying to connect to components!"

	while True:
		for addr in address_elevator:
			if (addr > my_address) and (addr not in address): 
				try:
					conn = network.Create_Socket(addr, 22290)		
				except:
					print "I did not manage to connect to ", addr
				else:
					connection.append(conn)
					address.append(addr)
					flag_component_alive.append(1)
					print "New Connected address:", address[-1]
					print "I am connected to ", len(connection), " components!" 

					thread.start_new_thread(Receive_From_Component,(conn, addr))
					thread.start_new_thread(Watchdog_Component_Alive,(conn, addr))

			time.sleep(1)

#---------------------------------------------------------------------------------------------------------
def Eliminate_Component_From_Lists(addr):
	global address
	global connection

	component_index = address.index(addr)

	connection.pop(component_index)
	address.pop(component_index)
	flag_component_alive.pop(component_index)

	print "I am now connected to ", len(connection), " components!"

#---------------------------------------------------------------------------------------------------------
def Watchdog_Component_Alive(conn, addr):
	global address
	global flag_component_alive

	while True:
		try:
			component_index = address.index(addr)
		except:
			# Dead component (it was removed from the lists)
			break
		else:
			if flag_component_alive[component_index] == 0:
				# Dead component
				print addr, "is dead (Network or Power lost)"
				Eliminate_Component_From_Lists(addr)
				break
			else:
				# Alive component
				flag_component_alive[component_index] == 0
				time.sleep(3)
		
#---------------------------------------------------------------------------------------------------------
def Receive_From_Component(conn, addr):
	global address
	global flag_component_alive

	print "I am receiving from ", addr

	while True:
		message = network.Receive_Message(conn)

		if not message:
			# Dead component
			print addr, "is dead (Null message received)"
			Eliminate_Component_From_Lists(addr)
			break
		else:
			# Alive component
			print "I received from ", addr, "the message: ", message
			flag_component_alive[address.index(addr)] = 1
			
		
#---------------------------------------------------------------------------------------------------------
#def Watchdog_Client_Alive(conn, addr):

#def Main_Thread(conn, addr):

#add process pair
#---------------------------------------------------------------------------------------------------------
print 'I am ', my_address

thread.start_new_thread(Listen_To_Components,())
thread.start_new_thread(Connect_To_Components,())

while True:
	for conn in connection:
		network.Send_Message(conn, "[Lemur] IAA")

	time.sleep(2)
