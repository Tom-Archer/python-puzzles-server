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

IMAGE_SIZE = 900
PIXEL_SIZE = 5

KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log(__name__, level='INFO', file='infoc.log')

BACKGROUND_COLOR = (0.3, 0.3, 0.3, 1.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=20)
HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
CAMERA = pi3d.Camera(is_3d=False)

class ImageRandomiser(pi3d.Points):
    def __init__(self, texture_path, image_size, pixel_size, width, height):
        texture = Image.open(texture_path)
        texture_size = texture.size

        self.num_pixels = int(image_size / pixel_size)
        point_size = 1.0 * float(pixel_size / texture_size[0])

        shader = pi3d.Shader("uv_pointsprite")
        img = pi3d.Texture(texture_path, mipmap=False, i_format=pi3d.GL_RGBA, filter=pi3d.GL_NEAREST)

        self.loc = np.zeros((self.num_pixels*self.num_pixels, 3))
        uv = np.zeros((self.num_pixels*self.num_pixels, 2))
        
        # Constant arrays for efficiency
        sorted_row = np.arange(self.num_pixels)
        self.sorted_x_positions = np.arange(-width + pixel_size/2, -width + pixel_size/2 + (pixel_size * self.num_pixels), pixel_size)
        sorted_y_positions = np.arange(height - pixel_size/2, height - pixel_size/2 - (pixel_size * self.num_pixels), -pixel_size)
        texture_positions = np.linspace(0, point_size * self.num_pixels, self.num_pixels, False)
        # make this accessible so we can grab rows
        self.initial_positions = np.random.rand(self.num_pixels, self.num_pixels).argsort()
        
        # Set starting positions
        for j in range(0, self.num_pixels):
            for i in range(0, self.num_pixels):
                index = self.initial_positions[j,i]
                self.loc[index+j*self.num_pixels,0] = self.sorted_x_positions[i]
                self.loc[index+j*self.num_pixels,1] = sorted_y_positions[j]
                self.loc[index+j*self.num_pixels,2] = 0.999 # no scaling

                # Set textures
                uv[index+j*self.num_pixels,0] = texture_positions[index] 
                uv[index+j*self.num_pixels,1] = texture_positions[j]

        # Rotation is not required.
        rot = np.zeros((self.num_pixels*self.num_pixels, 3)) # :,0 for rotation
        rot[:,1] = 999.999 # :,1 R, G
        rot[:,2] = 999.999 # :,2 B, A

        super(ImageRandomiser, self).__init__(camera=CAMERA, vertices=self.loc, normals=rot, tex_coords=uv,
                           point_size=pixel_size)
        
        self.set_draw_details(shader, [img])
        self.unif[48] = point_size
                
    def update(self, row_list):
        #update positions
        for row in row_list:
            self.loc[row*self.num_pixels:(row+1)*self.num_pixels,0] = self.sorted_x_positions
      
        # re_init
        self.buf[0].re_init(pts=self.loc) # reform opengles array_buffer
        
        #if time.time() > next_time:
        #    LOGGER.info("FPS: %4.1f", (tick / 2.0))
        #    tick=0
        #    next_time = time.time() + 2.0
        #tick+=1



points = ImageRandomiser("MasterclassImage960.png", IMAGE_SIZE, PIXEL_SIZE, HWIDTH, HHEIGHT)

remaining_rows = list(range(0, points.num_pixels))


LOGGER.info('Starting SpriteMasterclass')
started = False
while DISPLAY.loop_running():
    try:
        # draw
        points.draw()

        if len(remaining_rows) == 0:
            started = False

        if started:
            # update positions
            row = remaining_rows.pop(random.randint(0, len(remaining_rows)-1))
            points.update([row])

        # parse keypresses
        k = KEYBOARD.read()
        if k > -1:
            if k == 27:
                KEYBOARD.close()
                DISPLAY.stop()
                break
            if k == 32:
                started = True
                
    except Exception as e:
        KEYBOARD.close()
        DISPLAY.stop()
        LOGGER.info(str(e))
