# Go to the desired floor(variable desired_floor)
# To Do: Move the elevator initially to any floor - When it is under the first floor it will still try to go down to the next floor - It should go up to the first floor

import time
from ctypes import *
libelev = CDLL("./libelev.so")

elev_motor_direction = {'DOWN': -1, 'STOP': 0, 'UP': 1}
elev_lamp = {'BUTTON_CALL_UP': 0, 'BUTTON_CALL_DOWN': 1, 'BUTTON_COMMAND': 2}

libelev.elev_init()

# Go down to any floor 
while libelev.elev_get_floor_sensor_signal() == -1:
	libelev.elev_set_motor_direction(elev_motor_direction['DOWN'])
libelev.elev_set_motor_direction(elev_motor_direction['STOP'])

# Go to the desired floor
desired_floor = 3

while True:
	current_floor = libelev.elev_get_floor_sensor_signal()

	if current_floor == desired_floor:
		libelev.elev_set_motor_direction(elev_motor_direction['STOP'])
	else:
		if current_floor < desired_floor and current_floor != -1:
			libelev.elev_set_motor_direction(elev_motor_direction['UP'])
		else:
			if current_floor > desired_floor and current_floor != -1:
				libelev.elev_set_motor_direction(elev_motor_direction['DOWN'])
