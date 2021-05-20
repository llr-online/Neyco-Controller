# coding: utf-8
import sys, time
from pymodbus.client.sync import ModbusSerialClient

# code for a decorator that put a try catch around the function
# the idea is to return True if everything is fine or the error message otherwise
def trycatch(func):
    errors = (Exception, )
    def wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
            if r:
                print(r)
            else:
                return True
        except errors as e:
            return repr(e)
    return wrapper

class Neyco(object):
    """
    class create to interact with the Neyco controler. It uses a modbus rtu protocol
    """

    neyco_dict = {
        0x0a: "actual speed ",
        0x0b: "z actual position",
        0x0c: "speed setting",
        0x0d: "z position setting",
        0x1a: "error code",
        0x1e: "z axis origin return status",
        0x1f: "z axis motor status",
        0x26: "functionnal error code",
        0x09: "action command",
        0xa1: "set speed",
        0xa5: "set position"
    }

    def __init__(self, port="/dev/ttyUSB0"):
        """
        init the connection since no parameters are really customizable except for port

        :param port: The port is device is connected to usually /dev/ttyS0
        """

        self.client = ModbusSerialClient(method="rtu",
                                         port=port,
                                         baudrate=9600,
                                         bytesize=8,
                                         parity="N",
                                         stopbits=1)
        self.client.connect()

        retval = self.client.read_holding_registers(0x000C, 0x0001, unit=0x01)
        if retval.isError():
            print("No device found on port %s\nAborting" % port)
            sys.exit(0)

    def _write(self,address , value):
        """

        :param address:
        :param value:
        :return:
        """
        r = self.client.write_register(address, value, unit=0x01)
        if r.isError():
            return "Error"
        else:
            return True

    def home(self):
        """
        Home

        :return:
        """
        self._write(0x9, 1)
        time.sleep(0.5)
        while self.client.read_holding_registers(0x1f, 0x01, unit=0x01).registers[0]:
            pass
        if self.client.read_holding_registers(0x1e, 0x01, unit=0x01).registers[0]:
            return "homing done"
        else:
            return "homing STOPPED"

    def move_to(self, position, progress=False):
        """
        move to a given position and wait until it's finished.

        :param position: float position to reach in mm from 0 to 150
        :param progress: boolean if true then print position.
        :return:
        """

        if not self._set_position(position):
            return "cannot move to position %f" % position
        time.sleep(1)
        self.run()
        time.sleep(1)
        while self.client.read_holding_registers(0x1f, 0x01, unit=0x01).registers[0]:
            if progress:
                print(self.client.read_holding_registers(0x0b, 0x01, unit=0x01).registers[0])
            else:
                time.sleep(0.1)
        return "position reached"

    def run(self):
        """
        move to the position stored.

        :return: 
        """
        self._write(0x9, 2)

    def up(self):
        """
        move up according to the interface that is down in fact

        :return:
        """
        self._write(0x9, 5)

    def down(self):
        """
        move down that is according to the interface up.

        :return:
        """
        self._write(0x9, 4)

    def stop(self):
        """
        stop the movement

        :return:
        """
        self._write(0x9, 3)

    def clear_faults(self):
        """
        clear faults.

        :return:
        """
        self._write(0x9, 6)

    def reset(self):
        """
        reset

        :return:
        """
        self._write(0x9, 19)

    def get_errors(self):
        """
        Give the error value
        :return: an integer
        """
        return self.client.read_holding_registers(0x1a, 0x01, unit=0x01).registers[0]

    def get_is_homed(self):
        """
        has the motor been successfully homed
        :return: 0 Failure
                 1 Success
        """
        return self.client.read_holding_registers(0x1e, 0x01, unit=0x01).registers[0]

    def get_is_moving(self):
        """
        is the motor running
        :return: 0 Stop
                 1 Run
        """
        return self.client.read_holding_registers(0x1f, 0x01, unit=0x01).registers[0]

    def get_actual_speed(self):
        """

        :return:
        """
        return self.client.read_holding_registers(0x0a, 0x01, unit=0x01).registers[0] / 10.

    # setter getter
    def _get_speed(self):
        """
        get the programmed speed
        :return:
        """
        return self.client.read_holding_registers(0x0c, 0x01, unit=0x01).registers[0]/10.

    @trycatch
    def _set_speed(self, s):
        """
        set the speed to use

        :param s: float in mm/s from 0.1 to 0.9
        :return:
        """
        if 0.1 <= s <= .9:
            self._write(0xa1, int(s * 10))
        else:
            return "speed should be in the 0.1 - 0.9 mm/s range here %f" % s

    speed = property(_get_speed,_set_speed)

    def _get_position(self):
        """
        get the programmed position

        :return:
        """
        return self.client.read_holding_registers(0x0d, 0x01, unit=0x01).registers[0] / 10.

    @trycatch
    def _set_position(self, p):
        """
        set the position to reach

        :param p:
        :return:
        """
        if 0 < p <= 150:
            self._write(0xa5, int(p * 10))
        else:
            return "position should be in the 0 - 150 mm range given %f" % (p)

    position = property(_get_position, _set_position)

    def get_actual_position(self):
        """

        :return:
        """
        return self.client.read_holding_registers(0x0b, 0x01, unit=0x01).registers[0] / 10.


if __name__ == "__main__":
    n = Neyco()
    n.move_to(12)
