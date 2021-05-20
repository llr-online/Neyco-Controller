Notes for the Neyco controler
=============================

Introduction
============

Programmable Logic Controller
-----------------------------
The neyco controller use a modbus rtu Programmable Logic controller (PLC) type XBC-DN20SU (https://download.factorymation.com/XGB/SU-Type/SU_Type_Manual.pdf)
with a positionning module XBF-PD02A (https://www.aspar.com.pl/katalogi/XBF-PD02A.pdf) the driver for the motor is a DM860D (?)

The cost of the PLC controller and positioning module is roughly 250 Euros each.

The PLC is programmed with a special software and the idea is more or less to define input (bouton, sensor, timer)  and
define output (motors, valves,...) and to define the behaviour of output according to the status of the inputs. For
example the motor should run when a limit switch has been reached. see https://www.youtube.com/watch?v=y2eWdLk0-Ho for
an example.

The PLC uses a RS485 bus


UI
--
The user interface is done with a TK6501 iP (?) WeinView. See https://www.weintek.com/globalw/Software/EasyBuilderPro.aspx
for how to program it.

RS485 and modbus
----------------
See http://www.yoctopuce.com/EN/article/petite-introduction-a-rs485-et-modbus for an introduction and also
https://www.modbustools.com/modbus.html for a more in depth description of the protocol.

RS485 is a serial line transmission protocol using different signal then RS232 and thus allowing many RS485 peripheral
on the same bus. Beware that you might need a terminator.

The modbus protocol is usually associated with the RS485. One specific aspect of the modbus is to add a Checksum to the
data and so it makes it less easy to send ascii frame than on serial bus.

The modbus as two flavor the ASCII one and the RTU which is a set of binary frame.

What we need to know roughly to use modbus is that there are 4 types of MODBUS registers:

-    The coils, corresponding to on/off binary outputs, such as relays.
-    The input bits, corresponding to binary inputs (read only).
-    The input registers, corresponding to analog inputs (read only).
-    The holding registers, corresponding to analog parameters which can be changed.

which more or less corresponds to

-   01h for the coils
-   02h for the input bits
-   04h for the input registers
-   03h for the holding register

In our case we will need to use the holding register since the data have to be changed.

Since RS485 is not native on most computer one need to use an adapter and the one I used is FTDI USB-RS485-WE (
https://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_USB_RS485_CABLES.pdf )

Python
======
To interact with a PLC controller, as far as I understand, we will need to interact with the inputs and basically
changing their values.

There are five field to set

   unit   type of command command code  value        crc
    0x01     0x03 or 0x06   see below   see below   computed by the module
The action that can be performed are listed below with their value.


.. list-table:: Neyco controller command
   :widths: 30 15 15 5 35
   :header-rows: 1

   * - Action
     - command code
     - value
     - R/W
     - Return value or Action
   * - actual speed
     - 0x0a
     - 0x01
     - R
     - [1,9]
   * - "z actual position"
     - 0x0b
     - 0x01
     - R
     - [0,1500]
   * - speed setting
     - 0x0c
     - 0x01
     - R
     - [1,9]
   * - z position setting
     - 0x0d
     - 0x01
     - R
     - [0,1500]
   * - error code
     - 0x1a
     - 0x01
     - R
     - ?
   * - z axis origin return status
     - 0x1e
     - 0x01
     - R
     - 1,0 (Success, Failure)
   * - z axis motor status
     - 0x1f
     - 0x01
     - R
     - 1,0 (Run, Stop)
   * - functionnal error code
     - 0x26
     - 0x01
     - R
     - ?
   * - action command
     - 0x09
     - W
     - 0x01
     - Homing
   * -
     -
     -
     - 0x02
     - go to set position
   * -
     -
     -
     - 0x03
     - stop running
   * -
     -
     -
     - 0x04
     - rise the z axis
   * -
     -
     -
     - 0x05
     - descent the z axis
   * -
     -
     -
     - 0x06
     - clear z axis error
   * -
     -
     -
     - 0x19
     - Function key reset
   * - set speed
     - 0xa1
     - [1,9]
     - W
     - set speed
   * - set position
     - 0xa5
     - [0,1500]
     - W
     - Set position

Notes:

- The value are integers and the position of the decimal point is set. For example setting speed to 3 means setting speed to 0.3 mm/s. The same for position
- the Return value or Action indicates either the value that is returned if the type is R or the action if the type is W

To write a command the python code is::

   r = self.client.write_register(address, value, unit=0x01)

where r is the return value containing a method isError() to check if everything is fine

To read a data one needs to::

  r = self.client.read_holding_registers(0x1e, 0x01, unit=0x01)
  value = r.registers[0]

r contains also isError() and registers a list containing the values.



About the code
==============

requirements
------------
You need the pymodbus module to run this code. To use a virtualenv you need to type:

     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt 

neyco.py
--------
Is the core library implementing the function given above.


neyco_rpl.py
------------
Is a code for interacting with the translator via command line.::
 
     python ./neyco_repl.py 
     Simple command processor for Neyco controller
     prompt: help
 
     Documented commands (type help <topic>):
    
     EOF                  get_actual_speed  get_speed  is_homed      set_position  up
     down                 get_error_code    help       is_moving  set_speed   
     get_actual_position  get_position      home       run        stop        

To get some help you cant type help command::

     prompt: help up
     move up (up means going down !!)
     prompt: help run
     move to the set position

To move there are two ways. One is to set the position and then run::

     prompt: set_position 10
     prompt: run
     prompt: get_position
     10.0

Or send a up command and monitor the change of position and then stop::

     prompt: up
     prompt: get_actual_position
     20.5
     prompt: get_actual_position
     21.5
     prompt: get_actual_position
     22.5
     prompt: get_actual_position
     23.4
     prompt: get_actual_position
     24.5
     prompt: get_actual_position
     25.4
     prompt: stop
     prompt: get_actual_position
     29.0

     
 Note that in this case the position accessed by get_position is not changed (it is also visible in the interface of the controler in position settings)::

     prompt: get_position
     10.0
 
The homing is also possible::

     prompt: home
     homing done

     
