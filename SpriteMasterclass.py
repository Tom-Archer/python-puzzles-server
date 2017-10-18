#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Sprites rendered using a diy points class and special shader uv_spriterot.

This code builds on the SpriteMulti demo.
The information is used by the uv_spritemult shader as follows

  vertices[0]   x position of centre of point relative to centre of screen in pixels
  vertices[1]   y position
  vertices[2]   z depth but fract(z) is used as a multiplier for point size
  normals[0]    rotation in radians
  normals[1]    red and green values to multiply with the texture
  normals[2]    blue and alph values to multiply with the texture. The values
                are packed into the whole number and fractional parts of
                the float i.e. where R and G are between 0.0 and 0.999
                normals[:,2] = floor(999 * R) + G
  tex_coords[0] distance of left side of sprite square from left side of
                texture in uv scale 0.0 to 1.0
  tex_coords[1] distance of top of sprite square from top of texture

unif[48] is used to hold the size of the sprite square to use for texture
sampling.
"""

print("""
Space to start
ESC to quit
""")

import numpy as np
import random
import time
import pi3d
from PIL import Image

texture_file = "MasterclassImage960.png"
texture = Image.open(texture_file)
texture_size = texture.size

IMAGE_SIZE = 900
PIXEL_SIZE = 5

num_pixels = int(IMAGE_SIZE / PIXEL_SIZE)
point_size = 1.0 * float(PIXEL_SIZE / texture_size[0])

KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log(__name__, level='INFO', file='info.log')

BACKGROUND_COLOR = (0.3, 0.3, 0.3, 1.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=20)
HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)

CAMERA = pi3d.Camera(is_3d=False)
shader = pi3d.Shader("uv_pointsprite")

img = pi3d.Texture(texture_file, mipmap=False, i_format=pi3d.GL_RGBA, filter=pi3d.GL_NEAREST)
# i_format=pi3d.GL_LUMINANCE_ALPHA ## see what happens with a converted texture type
loc = np.zeros((num_pixels*num_pixels, 3))
uv = np.zeros((num_pixels*num_pixels, 2)) # u picnum.u v
#uv[:,:] = 0.0 # all start off same. uv is top left corner of square
positions = np.random.rand(num_pixels, num_pixels).argsort()
sorted_row = np.arange(num_pixels)

for j in range(0, num_pixels):
    for i in range(0, num_pixels):
        index = positions[j,i]
        loc[index+j*num_pixels,0] = -HWIDTH + (i * PIXEL_SIZE) + PIXEL_SIZE/2
        loc[index+j*num_pixels,1] = HHEIGHT - (j * PIXEL_SIZE) - PIXEL_SIZE/2
        loc[index+j*num_pixels,2] = 0.999 # no scaling

        # Set textures
        uv[index+j*num_pixels,0] = index * point_size
        uv[index+j*num_pixels,1] = j * point_size

# leave this alone
rot = np.zeros((num_pixels*num_pixels, 3)) # :,0 for rotation
rot[:,1] = 999.999 # :,1 R, G
rot[:,2] = 999.999 # :,2 B, A

points = pi3d.Points(camera=CAMERA, vertices=loc, normals=rot, tex_coords=uv,
                   point_size=PIXEL_SIZE)
points.set_draw_details(shader, [img])
points.unif[48] = point_size

started = False

remaining_rows = list(range(0, num_pixels))

tick=0
next_time = time.time()+2.0

LOGGER.info('Starting SpriteMasterclass')

while DISPLAY.loop_running():

    # draw
    points.draw()

    if len(remaining_rows) == 0:
        started = False

    if started:

        # update positions
        row = remaining_rows.pop(random.randint(0, len(remaining_rows)-1))
        positions[row] = sorted_row

        for i in range(0, num_pixels):
            index = positions[row,i]
            loc[index+row*num_pixels,0] = -HWIDTH + (i * PIXEL_SIZE) + PIXEL_SIZE/2
  
        ##### re_init
        points.buf[0].re_init(pts=loc) # reform opengles array_buffer

        if time.time() > next_time:
            LOGGER.info("FPS: %4.1f", (tick / 2.0))
            tick=0
            next_time = time.time() + 2.0
        tick+=1

    k = KEYBOARD.read()
    if k > -1:
        if k == 27:
            KEYBOARD.close()
            DISPLAY.stop()
            break
        if k == 32:
            started = True


