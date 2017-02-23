import thread
import time

import network
import elev_driver

address_elevator = ["129.241.187.152", "129.241.187.153", "129.241.187.142"]
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
print 'I am ', my_address

thread.start_new_thread(Listen_To_Components,())
thread.start_new_thread(Connect_To_Components,())

elev_driver.elev_driver_init()

while True:
	# Tell the others that I am alive
	for conn in connection:
		network.Send_Message(conn, "[Lemur] IAA")

	# Find the role in the network
	if not address:
		flag_master = 1
	else:
		if my_address < min(address):
			flag_master = 1
		else:
			flag_master = 0

	# Read the buttons of the elevator
	(button, floor) = elev_driver.elev_driver_poll_buttons()

	if flag_master == 1:
		# Master part
		print "I am the Master!"
		#pass
	else:
		# Slave part
		print "I am a Slave!"

		master_conn = connection[ address.index( min(address) ) ]

		if button != -2 and floor != -2:
			#print "Button ", button, "from floor ", floor, " has been pressed"
			network.Send_Message(master_conn, "[Lemur] " + str(button) + " " + str(floor))

	time.sleep(0.5)
