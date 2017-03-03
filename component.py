import thread
import time

import network
import elev_driver

address_elevator = ["129.241.187.153", "129.241.187.157"]
my_address = network.Get_IP_Address()
connection = []
address = []
flag_component_alive = []
component_status = [] # 1 = Busy, 0 = Free
my_status = 0 # 1 = Busy, 0 = Free
commands_queue = []
flag_assign_component_thread_created = 0

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
		component_status.append(0)

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
					component_status.append(0)
					print "New Connected address:", address[-1]
					print "I am connected to ", len(connection), " components!" 

					thread.start_new_thread(Receive_From_Component,(conn, addr))
					thread.start_new_thread(Watchdog_Component_Alive,(conn, addr))

			time.sleep(0.5)

#---------------------------------------------------------------------------------------------------------
def Eliminate_Component_From_Lists(addr):
	global address
	global connection

	component_index = address.index(addr)

	connection.pop(component_index)
	address.pop(component_index)
	flag_component_alive.pop(component_index)
	component_status.pop(component_index)

	print "I am now connected to ", len(connection), " components!"

#---------------------------------------------------------------------------------------------------------
def Watchdog_Component_Alive(conn, addr):
	global address
	global flag_component_alive

	while True:
		# Tell the others that I am alive
		network.Broadcast_Message(connection, "[Lemur] IAA")

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
				print addr, "is alive"
				flag_component_alive[component_index] = 0
				time.sleep(1)
		
#---------------------------------------------------------------------------------------------------------
def Receive_From_Component(conn, addr):
	global address
	global flag_component_alive
	global commands_queue

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
			
			message_items = message.split(" ")
			if message_items[0] == "[Lemur]":
				# One of our messages
				flag_component_alive[address.index(addr)] = 1

				if message_items[1] == "[Button]":
					button = int(message_items[2])
					floor = int(message_items[3])
					elev_driver.libelev.elev_set_button_lamp(button, floor, 1)
					if [item for item in commands_queue if item[0] == button and item[1] == floor] == []:
						commands_queue.append([button, floor, ""])

				if message_items[1] == "[Status]":
					if message_items[2] == "Busy":
						component_status[address.index(addr)] = 1
					else:
						if message_items[2] == "Free":
							component_status[address.index(addr)] = 0

				if message_items[1] == "[Assignment]":
					for command_item in commands_queue:
						if command_item[0] == int(message_items[2]) and command_item[1] == int(message_items[3]):
							command_item[2] = message_items[4]
					if my_address == message_items[4]:
						thread.start_new_thread(elev_driver.elev_driver_go_to_floor, (int(message_items[3]),))

				if message_items[1] == "[Accomplishment]":
					for command in commands_queue:
						if command[2] == addr:
							commands_queue.pop(commands_queue.index(command)) 
			
#---------------------------------------------------------------------------------------------------------
def Assign_Component():
	global my_status, component_status, commands_queue, flag_assign_component_thread_created

	while flag_master == 1:		
		# Check the commands queue
		for command in commands_queue:
			if command[2] == "":
				time.sleep(0.1)
				# It is an unhandled command	
				if my_status == 0:
					my_status = 1
					command[2] = my_address
					network.Broadcast_Message(connection, "[Lemur] " + "[Assignment] " + str(command[0]) + " " + str(command[1]) + " " + my_address)				
					thread.start_new_thread(elev_driver.elev_driver_go_to_floor, (command[1],))
				else:
					flag_free_component = 0 # 0 = All components are Busy, 1 = At least one component is Free
					while flag_free_component == 0:
						try:
							free_component_index = component_status.index(0)
						except:
							pass
						else:
							flag_free_component = 1
					component_status[free_component_index] = 1
					command[2] = address[free_component_index]
					network.Broadcast_Message(connection, "[Lemur] " + "[Assignment] " + str(command[0]) + " " + str(command[1]) + " " + address[free_component_index])

	flag_assign_component_thread_created = 0

#---------------------------------------------------------------------------------------------------------
def Execute_Command(floor, internal):
	global my_status
	global commands_queue

	my_status = 1
	network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Busy")

	elev_driver.elev_driver_go_to_floor(floor)

	if internal == 0:
		# We have to pop out the accomplished command from the queue
		for command in commands_queue:
			if command[2] == my_address:
				commands_queue.pop(commands_queue.index(command))

		# Send a message to the others to pop out too from their queues
		network.Broadcast_Message(connection, "[Lemur] " + "[Accomplishment]")

	my_status = 0
	network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Free")

#------------------------------------------MAIN---------------------------------------------------------
print 'I am ', my_address

thread.start_new_thread(Listen_To_Components,())
thread.start_new_thread(Connect_To_Components,())

elev_driver.elev_driver_init()

while True:
	# Find the role in the network
	if not address:
		flag_master = 1
	else:
		if my_address < min(address):
			flag_master = 1
		else:
			flag_master = 0

	# Announce the others whether I am BUSY or FREE
	if elev_driver.elev_busy.acquire(False) == False:
		my_status = 1
		network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Busy")
	else:
		my_status = 0
		elev_driver.elev_busy.release()
		network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Free")

	# Read the buttons of the elevator
	(button, floor) = elev_driver.elev_driver_poll_buttons()
	if button != -2 and floor != -2:
		# A button was pressed
		if button == 2:
			# COMMAND button was pressed
			thread.start_new_thread(elev_driver.elev_driver_go_to_floor, (floor,))
		else:
			# UP or DOWN button was pressed
			network.Broadcast_Message(connection, "[Lemur] " + "[Button] " + str(button) + " " + str(floor)), "\0"
			if [item for item in commands_queue if item[0] == button and item[1] == floor] == []:
				commands_queue.append([button, floor, ""])

	if flag_master == 1:
		# Master part
		print "I am the Master!"
		if flag_assign_component_thread_created == 0:
			flag_assign_component_thread_created = 1
			thread.start_new_thread(Assign_Component,())
		
		#pass
	else:
		# Slave part
		print "I am a Slave!"
			

		#master_conn = connection[ address.index( min(address) ) ]

	#print "Others' Status: ", address, component_status
	#print "My Status: ", my_status

	print "Commands: ", commands_queue

	time.sleep(0.5)
