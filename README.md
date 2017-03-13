# Lemur_Project
TTK4145 - Real-Time Programming - Elevator Project

* The software controls *N* elevators working in parallel across *M* floors (by default set to *3* elevators and *4* floors)
* A computer connected to an elevator is called further on 'Component'
* 3 files are used in this project:
  * *component.py* contains the behaviour of a component
  * *network.py* contains the functions for handling the TCP network protocol
  * *elev_driver.py* contains the implemented functions connected with the elevator driver
  * *libelev.so* contains the functions of the elevator driver
* IP addresses of the components are hardcoded in *component.py* file
* All components are connected to each other via TCP connections (a component initiates with a connection only if the others IP is bigger - *Connect_To_Components* thread) (in the *Listen_to_Component* thread, a component listens to connections from other components)
* The component with the smallest IP address (string comparsion) is the Master
* Messages are received and interpreted in *Receive_From_Component* thread. Each type of message is checked to have the required number of fields. If this condition is not respected it means 2 or more messages were sticked together and are ignored
* The Master component decides which component should handle each order
* Elevator buttons are polled in the *Main* function
* When an internal button is pressed, that component handles the order as soon it is free, not taking into account any external orders
* When an external button is pressed, that component send a *Button* type message to the other components (when this message is received, the lamp of the buttons are synchronized to show the same status)
* After an external command is finished, an *Accomplishment* type message is send to all the components
* All components add the new order in a Queue (for every command, in the queue are stored: the direction (button type), the desired floor, the IP of the component which handles the order and the time stamp (second) when the order is started to be handled)
* All components send *Status* messages in the *Send_Status* thread to others saying whether they are Busy or Free
* After handling an external order, the doors of the elevator are kept open for 3 seconds. After that, if no internal orders exist, an external order is handled (if exists)
* The Master component assigns in the *Assign_Component* thread the free component with the smallest IP to an unhandled order
* An order (internal or external) is handled in the *Execute_Command* thread
* When a new component joins the network, the order Queues of all components are synchronized by sending *Queue* type messages (in the *Listen_to_Component* and *Connect_To_Components* threads)
* Every component has a Watchdog thread (*Watchdog_Component_Alive*) for every component in the network in order to verify who is still alive and connected in the network (if no messages are received from a component in 3 seconds then that component is dead or disconnected and it is eliminated from the connections list)
* If a component is not connected anymore to the network, it continues to handle the received orders and accepts new ones
* When handling an order, the component checks if the order is accomplished in 20 seconds. If not, it means the elevator is stuck and the order is declared unassigned again by sending a *Stuck* type message (*Execute_Command* thread)
* The Master component checks if all the components are accomplished in 20 seconds. If an ordered is detected as being stuck then a *Stuck* type message is also send by the Master (in order to cover the case when the component which was supposed to handle that order died and didn't manage to send by itself the *Stuck* type message) (*Assign_Component* thread)
* After being Stuck, a component can handle a new order. If a component is Stuck 3 times then it is removed from the network (*Execute_Command* thread)
* The role of each component (Master or not) is rechecked continuosly in the *Main* function
* The handled orders which are older than 40 seconds are cleaned from the queue of each component (*Main* function) (covers the case when handled orders are propagated from one component from another when queue synchronization is done)
* Faults handled: network packet loss, loss of network connection, loss of power for both elevator motor and computer that controls an elevator, software crash.
* No orders are lost as long as at least one component is alive (due to the fact that every component stores all the orders in their own queue)
