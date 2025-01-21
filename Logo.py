from Code import *
import os
# Load the PNG image
base_dir = os.path.dirname(__file__)
image = pyglet.image.load((os.path.join(base_dir, 'Sprites','logo_white1.png')))
sprite = pyglet.sprite.Sprite(image,x=window.width//1.17,y=window.height//60,batch=batch)
sprite = pyglet.sprite.Sprite(image, batch=batch)

# Calculate the scale factor based on the window size and the image size
scale_factor = min(window.width / image.width, window.height / image.height) / 5
sprite.scale = scale_factor

# Position the sprite in the lower right corner of the window
sprite.x = window.width - sprite.width - 10  # 10 pixels padding from the right edge
sprite.y = 10  # 10 pixels padding from the bottom edge