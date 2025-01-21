import pyglet
from pyglet.window import key

stick_drift_x = 1.5259021896696368e-05  #stick-drift correction value x, can be changed
stick_drift_y = 1.5259021896696368e-05  #stick-drift correction value y, can be changed
joysticks = pyglet.input.get_joysticks()  
keys = key.KeyStateHandler()  #define keys as the keyStateHandler
jx =  0     #define joystick x and joystick y variables
jy = 0
sens = 0
joystick1_sim = False
joystick2_sim = False


def clamp(value, min_value, max_value):
    """
    Clamps the value within the specified range.

    Args:
        value: The value to be clamped.
        min_value: The minimum allowable value.
        max_value: The maximum allowable value.

    Returns:
        The clamped value.
    """

    return max(min_value, min(value, max_value))
class Control:
    def __init__(self):
        self.x
        self.y
 
    def no_joystick_connected():
            global joystick1_sim
            global joystick2_sim
            try: 
                if joysticks[0] and not joysticks[1]:
                    print(joysticks[0])
                    print('Only one joystick connected')
                    jstk1 = joysticks[0]
                    jstk2 = Joystick2()
                    
                    joystick1_sim = False
                    joystick2_sim = True
                    return jstk1, jstk2
            except:
                print('No Joystick connected')  
                jstk1 = Joystick1()
                jstk2 = Joystick2()
                joystick1_sim = True
                joystick2_sim = True
                return jstk1, jstk2




    def joyaxis_motion():
        """
        Takes the input from the joystick1 axes(x, y and z) that output values between -1 and 1 and converts that to 
        a consistent increase/decrease in the value to then be used by the different ..._movement() functions

        Input:
            joystick1.x(horizontal movement)
            joystick1.y(vertical movement)
            joystick2.rq(sensitivity)

        Returns:
            jx and jy as converted x and y values that consistently increase/decrease based on joystick input

        """
        # stick_drift_x and _y serve as correction for stick drift on the joystick.
        # You can change the values on top where they are defined.
        global jx
        global jy
        normalized_rq = (-joystick2.rq + 1.2) / 10   
        Control.joyaxis_motion.sens = normalized_rq            #rq axis on the joystick to control the sensitivity
        
        if abs(joystick1.x) > 0.08: #easier to control since it is less sensitive to small user inconsistencies 
            jx = jx - (joystick1.x * Control.joyaxis_motion.sens * 0.7 + stick_drift_x)
        else:
            jx = jx

        if abs(joystick1.y) > 0.08:
            jy = jy + (joystick1.y * Control.joyaxis_motion.sens * 0.7 + stick_drift_y)
        else:
            jy = jy
        
        return jx, jy
    
Control.joyaxis_motion.sens = 0
class Joystick1:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.buttons = [False] * 10

    def open(self):
        pass
    def update(self):
        self.x = (-1 if keys[key.A] else 1 if keys[key.D] else 0) 
        self.y = (-1 if keys[key.W] else 1 if keys[key.S] else 0) 
        self.buttons[0] = keys[key.ENTER]
        self.buttons[1] = keys[key._1]
        self.buttons[2] = keys[key._2]
        self.buttons[3] = keys[key._3]
        self.buttons[4] = keys[key._4]
        self.buttons[5] = keys[key._5]
        self.buttons[6] = keys[key._6]
        self.buttons[7] = keys[key._7]
        self.buttons[8] = keys[key._8]
        self.buttons[9] = keys[key._9]

class Joystick2:
    def __init__(self):
        self.rq = 0
        self.z = 0

    def update(self):
        
        if keys[key.LSHIFT]:
            if keys[key.LALT]:
                self.rq = -1
            else:
                self.rq = -0.4

        elif keys[key.LCTRL]:
            if keys[key.LALT]:
                self.rq = 0.99
            else:
                self.rq = 0.6
        else:
            self.rq = 0.2
        self.z += 0.03 if keys[key.RSHIFT] else -0.03 if keys[key.RCTRL] else 0
        self.z = clamp(self.z, -1, 1)

try:
    joystick1 = joysticks[0]                     #define and
    joystick2 = joysticks[1]                     #setup joysticks 1 and 2
    joystick1.open()
    joystick2.open()
except:
    joystick1, joystick2 = Control.no_joystick_connected()
    joystick1.open()


  


