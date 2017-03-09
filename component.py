import thread
import time
import network
import elev_driver

#---------------------------------------------------------------------------------------------------------
ADDRESS_ELEVATOR = ["129.241.187.152", "129.241.187.157", "129.241.187.48"]
PORT_NUMBER = 22290
STUCK_TIMES_THRESHOLD = 3

#---------------------------------------------------------------------------------------------------------
connection = []
address = []
commands_queue = []
flag_component_alive = []
component_status = [] # 1 = Busy, 0 = Free
my_status = 0 # 1 = Busy, 0 = Free
my_stuck_times = 0
old_flag_master = -1
flag_assign_component_thread_created = 0
my_address = network.Get_IP_Address()

#---------------------------------------------------------------------------------------------------------
def Listen_To_Components():
	global connection
	global address

	s = network.Bind_Socket(my_address, PORT_NUMBER)

	while True:
		s.listen(1)

		(conn, addr) = network.Accept_Connection(s)
		addr = addr[0]		

		connection.append(conn)		
		address.append(addr)
		flag_component_alive.append(1)
		component_status.append(0)

		print "Connected to: ", addr

		thread.start_new_thread(Receive_From_Component,(conn, addr))
		thread.start_new_thread(Watchdog_Component_Alive,(conn, addr))

		## Synchronize queues (sending)
		for command in commands_queue:
			network.Broadcast_Message(connection, "[Lemur] " + "[Queue] " + str(command[0]) + " " + str(command[1]) + " " + command[2])
			time.sleep(0.1)

#---------------------------------------------------------------------------------------------------------
def Connect_To_Components():
	global connection
	global address

	while True:
		for addr in ADDRESS_ELEVATOR:
			if (addr > my_address) and (addr not in address): 
				try:
					conn = network.Create_Socket(addr, PORT_NUMBER)		
				except:
					pass
				else:
					connection.append(conn)
					address.append(addr)
					flag_component_alive.append(1)
					component_status.append(0)

					print "Connected to: ", addr

					thread.start_new_thread(Receive_From_Component,(conn, addr))
					thread.start_new_thread(Watchdog_Component_Alive,(conn, addr))

					## Synchronize queues (sending)
					for command in commands_queue:
						network.Broadcast_Message(connection, "[Lemur] " + "[Queue] " + str(command[0]) + " " + str(command[1]) + " " + command[2])
						time.sleep(0.1)

			time.sleep(0.5)

#---------------------------------------------------------------------------------------------------------
def Eliminate_Component_From_Lists(addr):
	global connection
	global address

	component_index = address.index(addr)

	connection.pop(component_index)
	address.pop(component_index)
	flag_component_alive.pop(component_index)
	component_status.pop(component_index)

	print "Disconnected from: ", addr

#---------------------------------------------------------------------------------------------------------
def Watchdog_Component_Alive(conn, addr):
	global address
	global flag_component_alive

	while True:
		try:
			component_index = address.index(addr)
		except:
			break
		else:
			if flag_component_alive[component_index] == 0:
				# Dead component
				Eliminate_Component_From_Lists(addr)
				break
			else:
				# Alive component
				flag_component_alive[component_index] = 0
				time.sleep(3)
		
#---------------------------------------------------------------------------------------------------------
def Receive_From_Component(conn, addr):
	global address
	global flag_component_alive
	global commands_queue

	while True:
		message = network.Receive_Message(conn)

		if not message:
			# Dead component
			Eliminate_Component_From_Lists(addr)
			break
		else:
			# Alive component
			print "I received from ", addr, "the message: ", message
			
			message_items = message.split(" ")
			if message_items[0] == "[Lemur]":
				# Check if the message has the unique tag for our group

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
					button = int(message_items[2])
					floor = int(message_items[3])
					ip = message_items[4]
					for command_item in commands_queue:
						if command_item[0] == button and command_item[1] == floor:
							command_item[2] = ip
					if my_address == ip:
						thread.start_new_thread(Execute_Command, (button, floor, 0))

				if message_items[1] == "[Accomplishment]":
					floor = int(message_items[2])
					for command in commands_queue:
						if command[2] == addr and command[1] == floor:
							commands_queue.pop(commands_queue.index(command)) 
							elev_driver.libelev.elev_set_button_lamp(elev_driver.ELEV_LAMP['BUTTON_CALL_UP'], floor, 0)
							elev_driver.libelev.elev_set_button_lamp(elev_driver.ELEV_LAMP['BUTTON_CALL_DOWN'], floor, 0)

				if message_items[1] == "[Queue]":
					button = int(message_items[2])
					floor = int(message_items[3])
					ip = message_items[4]
					flag_same_command_found = 0
					for command in commands_queue:
						if command[0] == button and command[1] == floor:
							flag_same_command_found = 1
							if ip != "":
								command[2] = ip
							break
					if flag_same_command_found == 0:
						commands_queue.append([button, floor, ip])

				if message_items[1] == "[Stuck]":
					button = int(message_items[2])
					floor = int(message_items[3])
					for command in commands_queue:
						if command[2] == addr and command[1] == floor:
							commands_queue.pop(commands_queue.index(command)) 
					commands_queue.append([button, floor, ""])
									
#---------------------------------------------------------------------------------------------------------
def Assign_Component():
	global my_status
	global component_status
	global commands_queue
	global flag_assign_component_thread_created

	while flag_master == 1:		
		for command in commands_queue:
			if command[2] == "":
				flag_free_component = 0 # 0 = All components are Busy, 1 = At least one component is Free

				while flag_free_component == 0:	
					time.sleep(0.1)

					if my_status == 0:
						# The Master takes the order
						flag_free_component = 1
						my_status = 1
						command[2] = my_address
						network.Broadcast_Message(connection, "[Lemur] " + "[Assignment] " + str(command[0]) + " " + str(command[1]) + " " + my_address)
						thread.start_new_thread(Execute_Command, (command[0], command[1], 0))
					else:
						# Try to find a free component
						try:
							free_component_index = component_status.index(0)
						except:
							pass
						else:
							# A free component was found and the order is assigned to it
							flag_free_component = 1
							component_status[free_component_index] = 1
							command[2] = address[free_component_index]
							network.Broadcast_Message(connection, "[Lemur] " + "[Assignment] " + str(command[0]) + " " + str(command[1]) + " " + address[free_component_index])

	flag_assign_component_thread_created = 0

#---------------------------------------------------------------------------------------------------------
def Execute_Command(button, floor, internal):
	# internal = 1 if it is an internal (cab) command, 0 if it is an external (hall) command

	global my_status
	global commands_queue
	global my_stuck_times

	my_status = 1
	network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Busy")

	if internal == 0:
		if elev_driver.elev_driver_go_to_floor(floor) == -1:
			# It is stuck
			my_stuck_times = my_stuck_times + 1
			print my_address, "is STUCK for the ", my_stuck_times, " time"

			network.Broadcast_Message(connection, "[Lemur] " + "[Stuck] " + str(button) + " " + str(floor))
			commands_queue.append([button, floor, ""])

			for command in commands_queue:
				if command[2] == my_address and command[1] == floor:
					commands_queue.pop(commands_queue.index(command))

			elev_driver.libelev.elev_set_motor_direction(elev_driver.ELEV_MOTOR_DIRECTION['STOP'])

			if my_stuck_times < STUCK_TIMES_THRESHOLD:
				time.sleep(3)
				elev_driver.elev_driver_init_after_stuck()

				my_status = 0
				network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Free")
		else:
			# It is not stuck
			for command in commands_queue:
				if command[2] == my_address and command[1] == elev_driver.libelev.elev_get_floor_sensor_signal():
					commands_queue.pop(commands_queue.index(command))

			network.Broadcast_Message(connection, "[Lemur] " + "[Accomplishment] " + str(command[1]))

			elev_driver.libelev.elev_set_button_lamp(0, floor, 0)
			elev_driver.libelev.elev_set_button_lamp(1, floor, 0)

			my_status = 0
			network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Free")
	else:
		elev_driver.elev_driver_go_to_floor(floor)

		elev_driver.libelev.elev_set_button_lamp(elev_driver.ELEV_LAMP['BUTTON_COMMAND'], floor, 0)

		my_status = 0
		network.Broadcast_Message(connection, "[Lemur] " + "[Status] " + "Free")

#------------------------------------------MAIN---------------------------------------------------------
print 'I am ', my_address

elev_driver.elev_driver_init()

thread.start_new_thread(Listen_To_Components,())
thread.start_new_thread(Connect_To_Components,())

while True:
	network.Broadcast_Message(connection, "[Lemur] [Alive]")

	# Find the role in the network (the Master is the one with the smallest IP)
	if not address:
		flag_master = 1 # 1 if it is the Master, 0 if it is not
	else:
		if my_address < min(address):
			flag_master = 1
		else:
			flag_master = 0

	(button, floor) = elev_driver.elev_driver_poll_buttons()
	if button != -2 and floor != -2:
		if button == elev_driver.ELEV_BUTTON['BUTTON_COMMAND']:
			thread.start_new_thread(Execute_Command, (button, floor, 1))
		else:
			network.Broadcast_Message(connection, "[Lemur] " + "[Button] " + str(button) + " " + str(floor))
			if [item for item in commands_queue if item[0] == button and item[1] == floor] == []:
				commands_queue.append([button, floor, ""])

	if flag_master == 1:
		# Master part
		if old_flag_master != flag_master:
			print "I am the Master!"

		if flag_assign_component_thread_created == 0:
			flag_assign_component_thread_created = 1
			thread.start_new_thread(Assign_Component,())
	else:
		# Slave part
		if old_flag_master != flag_master:
			print "I am a Slave!"
			
	#print "Commands: ", commands_queue

	old_flag_master = flag_master

	time.sleep(0.5)
