from pythonosc import udp_client
import pyglet
from pyglet.gl import *
from Math_trigonometry import *
from pyglet.window import key
from pyglet import font
from pyglet.window import mouse
from Control import *
import os

base_dir = os.path.dirname(__file__)
MA3_IP = "192.168.1.33"  # Replace with your GrandMA3 console's IP address
MA3_OSC_PORT = 8000    # OSC port for GrandMA3


client = udp_client.SimpleUDPClient(MA3_IP, MA3_OSC_PORT) #client for OSC messages to work
pan = 0     #define pan, tilt, sens, zoom and intensity
tilt = 0

intensity = 0                
                  
                  
window = pyglet.window.Window(fullscreen = True) #define window, fullscreen can be changed to width = ... , height = ....
window.set_caption("Lightcontroller")            #to enable windowed mode with the specified resolution
font.add_file(os.path.join(base_dir, 'Sprites', 'helvetica', 'Helvetica.ttf'))  #font for the labels
helvetica = font.load('Helvetica', 36)                #font size for the labels



batch = pyglet.graphics.Batch()                  #setup of "batches" for efficient graphics processing
label = pyglet.graphics.Batch()
calibration_batch = pyglet.graphics.Batch()
selection = pyglet.graphics.Batch()
control = pyglet.graphics.Batch()
outofbounds = pyglet.graphics.Batch()
input_batch = pyglet.graphics.Batch()
fixture_id_batch = pyglet.graphics.Batch()


window.push_handlers(keys)

x_middle = window.width // 2                    #middle of the window values
y_middle = window.height // 2

stage_origin = window.width//6, window.height//3        #bottom-left corner of the stage displayed on screen
background = pyglet.shapes.Rectangle(0,0, window.width, window.height, color=(100,100,100), batch=batch)
Stage = pyglet.shapes.Rectangle(stage_origin[0],stage_origin[1], window.width//1.5, window.height//1.7, color = (70,70,70), batch=batch) #stage displayed on screen
stage_middle = Stage.x + Stage.width / 2, Stage.y + Stage.height / 2    #center of the stage displayed on screen
origin = stage_origin[0], stage_origin[1]

jstk_rect = pyglet.shapes.Circle(jx, jy, window.height // 25, color=(255,0,0, 150), batch=batch)

offset = 90   #offset value if the moving head doesn't align with the stage in its home position

coordinates = []


def cartesian_movement(jstk_cart_position):
    """
    Takes the x and y values from the jstk_rectangle_movement() function and transforms them to output values in the 0-100
    range if the red jstk_rectangle is somewhere on the stage.

    Args:
        jstk_cart_position: The initial position of the rectangle on the stage
    
    Input:
        The joyx and joyy values from the jstk_rectangle_movement() function

    Returns:
        The adjusted x and y values of the jstk_rectangle to be further used in the translate_to_quadrilateral() function
    """
    global cart_x
    global cart_y
    
    cart_joyx, cart_joyy = Control.joyaxis_motion()
    
    jstk_cart_position = jstk_cart_position[0] + cart_joyx * window.width/175, jstk_cart_position[1] + cart_joyy * window.height / 175      
    
    cart_x, cart_y = (-jstk_cart_position[0] + window.width/6)/(window.width/151), (-jstk_cart_position[1] + window.height/3)/(window.height/171)  # /bysomething numbers are there so that in the end
    return jstk_cart_position, cart_x, cart_y                                                                                                      # bottom-left of the stage is 0,0 and top-right 100,100



def rectangle_movement():
    """Takes the positional value of the cartesian_movement() function and applies it to the pyglet jstk_rectangle shape"""
    position = cartesian_movement(origin)
    jstk_rect.anchor_position = position[0][0] - window.width / 3, position[0][1] - window.height / 1.5
    jstk_rect.radius = (light_parameters.zoom + 10) * window.height / 900            #radius scales with zoom
    return position[1], position[2]



def spherical_to_cartesian():
    """
    Takes the spherical coordinates(pan/tilt) and translates them to a cartesian coordinate system

    Input(no arguments): 
        Global Pan
        Global Tilt
        z (Height: can be chosen at random since the height is constant
        and therefore cancels out when transforming back to spherical)

    Returns:
        x and y in the cartesian coordinate system
    """

    global x
    global y
    z = 4
    x = (Math_Trigo.sine(pan-offset) * Math_Trigo.tan(tilt) * z)      
    y = (Math_Trigo.cosine(pan-offset) * Math_Trigo.tan(tilt) * z)
    return x, y



def light_parameters():
    """
    Takes the input from the joystick2 axes and converts it to usable values that
    can then be sent as an OSC command and displayed as a label in the interface

    Input:
        joystick2.rq
        joystick2.z

    the final parameters "intensity" and "zoom" are assigned as global
    """
    global intensity    #intensity is not used right now, will add possibility to change between sensitivity and intensity on the joytick axis in the future
    light_parameters.zoom = 0
    normalized_z = (joystick2.z + 1) / 2
    #intensity = normalized_rq * 100
    light_parameters.zoom = (normalized_z * 57.5) + 2.5   #multiplicator and + 2.5 is so that minimum zoom is 2 and maximum zoom is 60

light_parameters.zoom = 0  #initial value for zoom

def send_OSC():
    """
    sends the OSC Message based on joystick input to control the designated fixture

    Adjusts and sends the jx and jy values from the joyaxis_motion() function
    """

    global pan
    global tilt


    pan = jx  
    tilt = -jy * 0.7


    client.send_message("/gma3/cmd", f'At {light_parameters.zoom} Attribute "Zoom"')     #This OSC message structure is tailored specifically for grandMA3 consoles.
    client.send_message("/gma3/cmd", f'At {pan} Attribute "Pan"')       #it can be changed to control other consoles, but send_cartesian_OSC function will also have to be changed.
    client.send_message("/gma3/cmd", f'At {tilt} Attribute "Tilt"')     #it is essential that in the OSC settings of the grandMA3 the "prefix" is labeled "gma3"


def on_key_press(self, symbol, modifiers):

    if symbol == pyglet.window.key.SPACE:
        print("Confirmed text:", self.input_text)
        self.input_text = ""  # Clear the input for next entry
    elif symbol == pyglet.window.key.BACKSPACE:
        self.input_text = self.input_text[:-1]  # Remove last character
    else:
        self.input_text += chr(symbol)  # Add typed character to the string

    label.text = self.input_text  # Update the label text



