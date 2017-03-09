import threading
import time
import datetime

from ctypes import *
libelev = CDLL("./libelev.so")

#---------------------------------------------------------------------------------------------------------
N_FLOORS = 4
N_BUTTONS = 3
DOOR_OPEN_TIME = 3
ELEVATOR_STUCK_THRESHOLD = 10
INIT_POSITION_THRESHOLD = 5000
ELEV_MOTOR_DIRECTION = {'DOWN': -1, 'STOP': 0, 'UP': 1}
ELEV_LAMP = {'BUTTON_CALL_UP': 0, 'BUTTON_CALL_DOWN': 1, 'BUTTON_COMMAND': 2}
ELEV_BUTTON = {'BUTTON_CALL_UP': 0, 'BUTTON_CALL_DOWN': 1, 'BUTTON_COMMAND': 2}
BUTTON_STATUS = {'UNPRESSED' : 0, 'PRESSED' : 1}

#---------------------------------------------------------------------------------------------------------
old_button_signal = []
elev_busy = threading.Lock()

#---------------------------------------------------------------------------------------------------------
def elev_driver_init():
	global old_button_signal

	libelev.elev_init()	

	old_button_signal = [[0 for floor in range(0, N_FLOORS)] for button in range(0, N_BUTTONS)]
	
	# Initialize the position of the Elevator
	counter = 0
	while libelev.elev_get_floor_sensor_signal() == -1 and counter < INIT_POSITION_THRESHOLD:
		counter += 1
		libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['DOWN'])
		
	while libelev.elev_get_floor_sensor_signal() == -1:
		libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['UP'])
	libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['STOP'])
	
	print "I initialized myself on the floor: ", libelev.elev_get_floor_sensor_signal()	

#---------------------------------------------------------------------------------------------------------
def elev_driver_init_after_stuck():
	# Reinitialize the position of the Elevator
	counter = 0
	while libelev.elev_get_floor_sensor_signal() == -1 and counter < INIT_POSITION_THRESHOLD:
		counter += 1
		libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['DOWN'])
		
	while libelev.elev_get_floor_sensor_signal() == -1:
		libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['UP'])
	libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['STOP'])
	
	print "I initialized myself on the floor: ", libelev.elev_get_floor_sensor_signal()		
		
#---------------------------------------------------------------------------------------------------------
def elev_driver_go_to_floor(desired_floor):
	elev_busy.acquire()

	start_seconds = datetime.datetime.now().second

	while True:
		current_seconds = datetime.datetime.now().second
		difference_seconds = current_seconds - start_seconds
		if difference_seconds < 0:
			difference_seconds = difference_seconds + 60
		
		if difference_seconds >= ELEVATOR_STUCK_THRESHOLD:
			# Elevator is stuck
			elev_busy.release()
			return -1
			
		current_floor = libelev.elev_get_floor_sensor_signal()

		if current_floor != -1:
			libelev.elev_set_floor_indicator(current_floor)
			
			if current_floor == desired_floor:
				libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['STOP'])

				libelev.elev_set_door_open_lamp(1)
				time.sleep(DOOR_OPEN_TIME)				
				libelev.elev_set_door_open_lamp(0)	
			
				break
			else:		
				if current_floor < desired_floor:
					libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['UP'])
				else:
					if current_floor > desired_floor:
						libelev.elev_set_motor_direction(ELEV_MOTOR_DIRECTION['DOWN'])

		time.sleep(0.1)

	elev_busy.release()

	return 0

#---------------------------------------------------------------------------------------------------------
def elev_driver_poll_buttons():
	global old_button_signal
	
	for button in range(0, N_BUTTONS):
		for floor in range(0, N_FLOORS):
			button_signal = libelev.elev_get_button_signal(button, floor)
			if button_signal == BUTTON_STATUS['PRESSED'] and old_button_signal[button][floor] == BUTTON_STATUS['UNPRESSED']:
				old_button_signal[button][floor] = BUTTON_STATUS['PRESSED']
				libelev.elev_set_button_lamp(button, floor, 1)
				return (button, floor)
			else:
				if button_signal == BUTTON_STATUS['UNPRESSED'] and old_button_signal[button][floor] == BUTTON_STATUS['PRESSED']:
					old_button_signal[button][floor] = BUTTON_STATUS['UNPRESSED'];

	return (-2, -2)
