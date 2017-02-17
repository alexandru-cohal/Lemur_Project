import time
from ctypes import *
libelev = CDLL("./libelev.so")

N_FLOORS = 4
N_BUTTONS = 3

elev_motor_direction = {'DOWN': -1, 'STOP': 0, 'UP': 1}
elev_lamp = {'BUTTON_CALL_UP': 0, 'BUTTON_CALL_DOWN': 1, 'BUTTON_COMMAND': 2}

old_button_signal = []

#---------------------------------------------------------------------------------------------------------
def elev_driver_init():
	libelev.elev_init()	
	
	global old_button_signal
	old_button_signal = [[0 for floor in range(0, N_FLOORS)] for button in range(0, N_BUTTONS)]
	
	# Initialize the position of the Elevator
	## The threshold of the counter should be modified according to the distances between the 3rd floor sensor and the upper switch and between the 1rd floor sensor and the down switch
	counter = 0
	while libelev.elev_get_floor_sensor_signal() == -1 and counter < 50000:
		counter += 1
		libelev.elev_set_motor_direction(elev_motor_direction['DOWN'])
		
	while libelev.elev_get_floor_sensor_signal() == -1:
		libelev.elev_set_motor_direction(elev_motor_direction['UP'])
	libelev.elev_set_motor_direction(elev_motor_direction['STOP'])
	
	print "I initialized myself on the floor: ", libelev.elev_get_floor_sensor_signal()	
	
	
#---------------------------------------------------------------------------------------------------------
def elev_driver_go_to_floor(desired_floor):
	while True:
		current_floor = libelev.elev_get_floor_sensor_signal()

		if current_floor != -1:
			libelev.elev_set_floor_indicator(current_floor)
			
			if current_floor == desired_floor:
				libelev.elev_set_motor_direction(elev_motor_direction['STOP'])
				print "I reached the desired floor: ", desired_floor
				break
			else:		
				if current_floor < desired_floor:
					libelev.elev_set_motor_direction(elev_motor_direction['UP'])
				else:
					if current_floor > desired_floor:
						libelev.elev_set_motor_direction(elev_motor_direction['DOWN'])
	
#---------------------------------------------------------------------------------------------------------
def elev_driver_poll_buttons():
	global old_button_signal
	
	while True:
		for button in range(0, N_BUTTONS):
			for floor in range(0, N_FLOORS):
				button_signal = libelev.elev_get_button_signal(button, floor)
				if button_signal == 1 and old_button_signal[button][floor] == 0:
					old_button_signal[button][floor] = 1
					libelev.elev_set_button_lamp(button, floor, 1)
					print "The button ", button, " from the floor ", floor, " is pressed!"
				else:
					if button_signal == 0 and old_button_signal[button][floor] == 1:
						old_button_signal[button][floor] = 0;

## TEST					
#elev_driver_init()
#elev_driver_go_to_floor(3)
#elev_driver_poll_buttons()