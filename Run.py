from pythonosc import udp_client
import pyglet
from pyglet.gl import *
from Code import *
from Calibration import *


current_state = 0
num_states = 2
def cycle():
    global current_state
    switch_button = joystick1.buttons[1]
    button_press = button_press_and_release(switch_button)
    if button_press == True:
        current_state = (current_state + 1) % num_states


def show_mode():
    cycle()
    if current_state == 0:
        light_parameters()
        bounds_state = out_of_bounds()
        if bounds_state == False:
            rectangle_movement()
            cartesian_to_spherical()
            send_cartesian_OSC()
            labels.update_labels()
            labels.show_mode_label.text = f"Show"
        elif bounds_state == True:
            cartesian_movement(origin)
        #send_cartesian_OSC()
        labels.update_labels()
        labels.show_mode_label.text = f"Show"
    elif current_state == 1:
        labels.update_labels()
        labels.show_mode_label.text = f"No_Output"


jstk_rect = pyglet.shapes.Rectangle(jx, jy, window.height // 15, window.height // 15, color=(255,0,0), batch=batch)


create_Fixtures(fixtures)
center_and_distribute_fixtures(fixture_shapes, fixture_labels)
def update():
    show_mode()
    

def on_draw(dt):
    window.clear()
    batch.draw()
    label.draw()
    update()    

on_draw(1)



pyglet.clock.schedule_interval(on_draw, 1/60.0)
pyglet.app.run()