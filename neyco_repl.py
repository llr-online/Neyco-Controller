from neyco import Neyco
import cmd


class NeycoREPL(cmd.Cmd):
    prompt = 'prompt: '
    intro = "Simple command processor for Neyco controller"

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.neyco = Neyco()

    def do_get_actual_position(self, args):
        'get the current position'
        print(self.neyco.get_actual_position())

    def do_get_position(self, args):
        'get the position to be reached'
        print(self.neyco.position)

    def do_set_position(self, args):
        'set the position given in mm in the range [0 150]'
        self.neyco.position = float(args)

    def do_get_actual_speed(self, args):
        'get the actual speed'
        print(self.neyco.speed)

    def do_get_speed(self, args):
        'get the speed setting'
        print(self.neyco.speed)

    def do_set_speed(self, args):
        'set the speed given in mm/s in the range [0.1 0.9] '
        self.neyco.speed = float(args)

    def do_up(self, args):
        'move up (up means going down !!)'
        self.neyco.up()

    def do_down(self, args):
        'move down (down means going up !!)'
        self.neyco.down()

    def do_home(self, args):
        'home the system'
        print(self.neyco.home())

    def do_stop(self, args):
        'stop the movement'
        self.neyco.stop()

    def do_run(self, args):
        'move to the set position'
        self.neyco.run()

    def do_is_homed(self, args):
        'Is the motor successfully homed'
        if self.neyco.get_is_homed():
            print("True")
        else:
            print("False")

    def do_is_moving(self, args):
        'is the motor running'
        if self.neyco.get_is_moving():
            print("True")
        else:
            print("False")

    def do_get_error_code(self, args):
        'get error codes'
        print(self.neyco.get_errors())

    def do_EOF(self, arg):
        'Quit the REPL'
        return True


if __name__ == '__main__':
    NeycoREPL().cmdloop()