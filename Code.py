
from pythonosc import udp_client
import pyglet
from pyglet.gl import *
import math



MA3_IP = "192.168.1.12"  # Replace with your GrandMA3 console's IP address
MA3_OSC_PORT = 8000    # Standard OSC port for GrandMA3


client = udp_client.SimpleUDPClient(MA3_IP, MA3_OSC_PORT)

# Basic OSC message structure
Fixture = 303
tilt = 0
pan = 0
# Example: Turning on fixture 1
stick_drift_x = 1.5259021896696368e-05
stick_drift_y = 1.5259021896696368e-05
joysticks = pyglet.input.get_joysticks()
assert joysticks, 'Kein Joystick verbunden'
joystick1 = joysticks[0]
joystick2 = joysticks[1]
joystick1.open()
joystick2.open()


window = pyglet.window.Window(height = 1000, width = 1500)
window.set_caption("Lightcontroller")

batch = pyglet.graphics.Batch()
label = pyglet.graphics.Batch()
calibration = pyglet.graphics.Batch()
selection = pyglet.graphics.Batch()
control = pyglet.graphics.Batch()
outofbounds = pyglet.graphics.Batch()

background = pyglet.shapes.Rectangle(0,0, window.width, window.height, color=(100,100,100), batch=batch)


fixture_labels = []
fixture_shapes = []
fixtures = 5
x_middle = window.width // 2
y_middle = window.height // 2
jx =  0
jy = 0
normalized_z = (-joystick1.z + 1) // 2
jstk_rect = pyglet.shapes.Rectangle(jx, jy, window.height // 15, window.height // 15, color=(255,0,0), batch=batch)



def create_Fixtures(fixtures):
    for i in range(fixtures):
        size = window.height // 10
        label = pyglet.text.Label(f"Fixture {i + 1}", x=0 + size // 2, y=0 + size // 2, font_size=window.height // 100, anchor_x='center', batch=batch, color=(0,0,0,150))
        fixture_labels.append(label)
        fixture = pyglet.shapes.Rectangle(0, 0, size, size, color=(255, 255, 255), batch=batch)
        fixture_shapes.append(fixture)

def center_and_distribute_fixtures(rectangles, labels):
    """Centers and distributes a list of rectangles within a window."""
    size = window.height // 10
    num_rects = len(rectangles)
    total_width = sum(rect.width for rect in rectangles)

    # Calculate spacing between rectangles
    available_space = window.width - total_width
    spacing = available_space / (num_rects + 1) if num_rects > 1 else 0

    # Calculate starting x position
    start_x = (window.width - total_width - spacing * (num_rects - 1)) / 2

    # Position each rectangle
    for i, rect in enumerate(rectangles):
        rect.x = start_x + i * (rect.width + spacing)
        rect.y = window.height // 2 - rect.height // 2  # Center vertically
        labels[i].x = rect.x + size // 2
        labels[i].y = rect.y + size // 2

def standard_movement():
    jstk_rect.postion = jstk_rectangle_movement()
    jstk_rect.anchor_position = jstk_rectangle_movement()[0] - x_middle, jstk_rectangle_movement()[1] - y_middle

def out_of_bounds():
    red_pan = int((abs(pan)-199)*2.857)
    red_tilt = int((abs(tilt)-79)*2.454)
    if abs(pan) <= 270 and abs(tilt) <= 135:
        send_OSC()
        standard_movement()
    elif abs(pan) > 270 or abs (tilt) > 135:
        send_OSC()
        joyaxis_motion()
        outofbounds.draw()

    if 255 > abs(pan) > 200:
        labels.pan_label.color = (255,-red_pan,-red_pan,255)
    if abs(pan) >= 255:
        labels.pan_label.color = (255,0,0,255)

    if 135 > abs(tilt) > 80:
        labels.tilt_label.color = (255,-red_tilt,-red_tilt,255)
    if abs(tilt) >= 135:
        labels.tilt_label.color = (255,0,0,255)

def FixtureSelect_Collision(): 

    for i in fixture_shapes:
        collision = check_collision(jstk_rect,i)
        if collision == True:
            #print(collision, fixture_shapes[i])
            pass
    
def check_collision(rect1, rect2):
    """Checks if two pyglet.shapes.Rectangle objects are colliding."""
        # Check for overlap in the x-axis
    if (-rect1.anchor_position[0] + rect1.width >= rect2.x) and (rect2.x + rect2.width >= -rect1.anchor_position[0]):
    # Check for overlap in the y-axis
        if (-rect1.anchor_position[1] + rect1.height >= rect2.y) and (rect2.y + rect2.height >= -rect1.anchor_position[1]):
            #print("Collision")
            return True
        else:
            #print("None")
            return False
    else:
        #print("None")
        return False

def light_parameters():
    global intensity
    global zoom
    normalized_rq = (-joystick2.rq + 1) / 2
    normalized_z = (joystick2.z + 1) / 2
    intensity = normalized_rq * 100
    zoom = (normalized_z * 57.5) + 2.5
    
    client.send_message("/gma3/cmd", f'At {zoom} Attribute "Zoom"')
    #print(f'{Fixture} At Pan {pan}')
    client.send_message("/gma3/cmd", f'At {intensity}')


def joyaxis_motion():
    # stick_drift_x and _y serve as correction for stick drift on the joystick.
    # You can change the values on top where they are defined.
    global sens
    global jx
    global jy
    normalized_z = (-joystick1.z + 1.2) / 4
    sens = normalized_z
    
    if abs(joystick1.x) > 0.1: #easier to control since it is less sensitive to small user inconsistencies 
        jx = jx - (joystick1.x * sens + stick_drift_x)
    else:
        jx = jx

    if abs(joystick1.y) > 0.1:
        jy = jy + (joystick1.y * sens + stick_drift_y)
    else:
        jy = jy
    #print(joystick1.x, joystick1.y)  
    return jx, jy

def jstk_rectangle_movement():

    joyx, joyy= joyaxis_motion()
    
    rectx = joyx * window.width // 700
    recty = joyy * window.height // 700
    
    return rectx, recty

def send_OSC():
    """sends the OSC Message based on joystick input to control the designated fixture"""
    global pan
    global tilt


    pan = jx  
    tilt = -jy * 0.7

    client.send_message("/gma3/cmd", f'At {pan} Attribute "Pan"')
    #print(f'{Fixture} At Pan {pan}')
    client.send_message("/gma3/cmd", f'At {tilt} Attribute "Tilt"')
    #print(f'{Fixture} At Tilt {tilt}')

intensity = 0
zoom = 0
sens = 0

def spherical_to_cartesian():
    z = 100
    global x
    global y
    x = (Math.sine(pan - 90) * Math.tan(tilt) * z)
    y = (Math.cosine(pan - 90) * Math.tan(tilt) * z)
    return x, y

class Labels():   
    def __init__(self):

        self.pan_label = pyglet.text.Label(f"Pan: {pan}", 
                font_name="Arial",
                font_size= window.height // 40,
                x= window.height // 50, 
                y=window.height - window.height // 28,  
                anchor_x="left", 
                anchor_y="top",
                batch = label)

        self.tilt_label = pyglet.text.Label(f"Tilt: {tilt}", 
                font_name="Arial",
                font_size= window.height // 40,
                x= window.height // 50, 
                y=window.height - window.height // 14.7,  
                anchor_x="left", 
                anchor_y="top",
                batch = label)

        self.sens_label = pyglet.text.Label(f"Sens: {sens}", 
                font_name="Arial",
                font_size= window.height // 40,
                x= window.height // 50, 
                y=window.height - window.height // 10,
                anchor_x="left", 
                anchor_y="top",
                batch = label)

        self.intens_label = pyglet.text.Label(f"Intens: {intensity}", 
                font_name="Arial",
                font_size= window.height // 40,
                x= window.height // 50, 
                y=window.height - window.height // 7.5,  
                anchor_x="left", 
                anchor_y="top",
                batch = label)

        self.zoom_label = pyglet.text.Label(f"Zoom: {zoom}", 
                font_name="Arial",
                font_size= window.height // 40,
                x= window.height // 50, 
                y=window.height - window.height // 5.94,  
                anchor_x="left", 
                anchor_y="top",
                batch = label)
        
        self.calibration_text = pyglet.text.Label(f"", 
                font_name="Arial",
                font_size= window.height // 20,
                x= x_middle, 
                y=window.height - window.height // 14,  
                anchor_x="center", 
                anchor_y="top",
                batch = calibration)
        
        self.x_label = pyglet.text.Label(f"X-Position:", 
                font_name="Arial",
                font_size= window.height // 40,
                x= window.height // 40, 
                y= window.height // 4,  
                anchor_x="left", 
                anchor_y="top",
                batch = batch)
        
        self.y_label = pyglet.text.Label(f"Y-Position:", 
                font_name="Arial",
                font_size= window.height // 40,
                x= window.height // 40, 
                y= window.height // 4.5,  
                anchor_x="left", 
                anchor_y="top",
                batch = batch)
        
        self.show_mode_label = pyglet.text.Label(f"", 
                font_name="Arial",
                font_size= window.height // 20,
                x= window.height // 40, 
                y= window.height // 3,  
                anchor_x="left", 
                anchor_y="top",
                batch = label)
        
        self.out_of_bounds_label = pyglet.text.Label(f"OUT OF BOUNDS", 
                color = (255, 0, 0, 255),
                font_name="Arial",
                bold = True,
                font_size= window.height // 15,
                x= window.height // 2.8, 
                y= window.height // 1.2,  
                anchor_x="left", 
                anchor_y="top",
                batch = outofbounds)
        
    def next_step(self, step):
        location = []
        one = "bottom_left"
        two = "bottom_right"
        three = "Top_left"
        four = "Top_right"
        location.append(one, two, three, four)
        labels.calibration_text.text = f"Please direct the Followspot-Light to the {location[0][step]} and press trigger"
        pass

    def update_labels(self):
        x, y = spherical_to_cartesian()
        labels.pan_label.text = f"Pan: {int(pan)}"
        labels.tilt_label.text = f"Tilt: {int(tilt)}"
        labels.sens_label.text = f"Sens: {int(sens * 198 - 8) }"
        labels.intens_label.text = f"Intens: {int(intensity)}"
        labels.zoom_label.text = f"Zoom: {int(zoom)}"
        labels.x_label.text = f"X-Position: {int(x)}"
        labels.y_label.text = f"Y-Position: {int(y)}"

    
class Math():

    def sine(degrees):
        """Calculates the sine of an angle given in degrees."""
        radians = math.radians(degrees)  # Convert degrees to radians
        sine_value = math.sin(radians)
        return sine_value   # Convert the result back to degrees

    def tan(degrees):
        """Calculates the tangent of an angle given in degrees"""
        radians = math.radians(degrees)
        tangent_value = math.tan(radians)
        return tangent_value

    def cosine(degrees):
        """Calculates the cosine of an angle given in degrees"""
        radians = math.radians(degrees)
        cosine_value = math.cos(radians)
        return cosine_value

#client.send_message("/gma3/Page1/Fader201",0)
labels = Labels()

