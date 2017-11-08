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

import numpy as np
import random
import time
import pi3d
from PIL import Image

class ImageRandomiser(pi3d.Points):
    def __init__(self, texture_path, width, height, pixel_size, camera):
        self.width = width
        self.height = height
    
        texture = Image.open(texture_path)
        texture_width = texture.size[0]
        texture_height = texture.size[1]

        if texture_width != texture_height:
            raise ValueError('The texture must be square.')

        if width > texture_width or height > texture_height:
            raise ValueError('The texture must be larger than the display area.')

        self.num_pixels_w = int(width / pixel_size)
        self.num_pixels_h = int(height / pixel_size)
        
        point_size = 1.0 * float(pixel_size / texture_width)

        shader = pi3d.Shader("uv_pointsprite")
        img = pi3d.Texture(texture_path, mipmap=False, i_format=pi3d.GL_RGBA, filter=pi3d.GL_NEAREST)

        self.loc = np.zeros((self.num_pixels_w*self.num_pixels_h, 3))
        uv = np.zeros((self.num_pixels_w*self.num_pixels_h, 2))
        
        # Constant arrays for efficiency
        sorted_row = np.arange(self.num_pixels_w)
        self.sorted_x_positions = np.arange(pixel_size/2, pixel_size/2 + (pixel_size * self.num_pixels_w), pixel_size)
        self.sorted_y_positions = np.arange(- pixel_size/2, - pixel_size/2 - (pixel_size * self.num_pixels_h), -pixel_size)
        texture_positions_x = np.linspace(0, point_size * self.num_pixels_w, self.num_pixels_w, False)
        texture_positions_y = np.linspace(0, point_size * self.num_pixels_h, self.num_pixels_h, False)
        self.initial_positions = np.random.rand(self.num_pixels_h, self.num_pixels_w).argsort()
        
        # Set starting positions
        for j in range(0, self.num_pixels_h):
            for i in range(0, self.num_pixels_w):
                index = self.initial_positions[j,i]
                self.loc[index+j*self.num_pixels_w,0] = self.sorted_x_positions[i]
                self.loc[index+j*self.num_pixels_w,1] = self.sorted_y_positions[j]
                self.loc[index+j*self.num_pixels_w,2] = 0.999 # no scaling

                # Set textures
                uv[index+j*self.num_pixels_w,0] = texture_positions_x[index] 
                uv[index+j*self.num_pixels_w,1] = texture_positions_y[j]

        # Rotation is not required.
        rot = np.zeros((self.num_pixels_w*self.num_pixels_h, 3)) # :,0 for rotation
        rot[:,1] = 999.999 # :,1 R, G
        rot[:,2] = 999.999 # :,2 B, A

        super(ImageRandomiser, self).__init__(camera=camera, vertices=self.loc, normals=rot, tex_coords=uv,
                           point_size=pixel_size)
        
        self.set_draw_details(shader, [img])
        self.unif[48] = point_size
                
    def update(self, row_list):
        # Update positions
        for row in row_list:
            if row < self.initial_positions.shape[0]:
                self.loc[row*self.num_pixels_w:(row+1)*self.num_pixels_w,0] = self.sorted_x_positions
      
        # re_init
        self.re_init(pts=self.loc) # reform opengles array_buffer

    def get_row(self, row):
        if row < self.initial_positions.shape[0]:
            return self.initial_positions[row]
        else:
            return None

    def reset(self):
        # Set starting positions
        for j in range(0, self.num_pixels_h):
            for i in range(0, self.num_pixels_w):
                index = self.initial_positions[j,i]
                self.loc[index+j*self.num_pixels_w,0] = self.sorted_x_positions[i]
                self.loc[index+j*self.num_pixels_w,1] = self.sorted_y_positions[j]
                self.loc[index+j*self.num_pixels_w,2] = 0.999 # no scaling

        # re_init
        self.re_init(pts=self.loc) # reform opengles array_buffer

if __name__ == '__main__':
    from status_display import StatusDisplay

    print("""
    Space to start
    ESC to quit
    """)
    
    IMAGE_SIZE = 900
    PIXEL_SIZE = 5

    KEYBOARD = pi3d.Keyboard()
    LOGGER = pi3d.Log(__name__, level='INFO', file='info.log')

    BACKGROUND_COLOR = (0.3, 0.3, 0.3, 1.0)
    DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=10)
    HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
    CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

    points = ImageRandomiser("MasterclassImage960.png", IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)
    status = StatusDisplay(925, -50, CAMERA)
    status.display_list(['team1','team2','team3','team4'])
    
    remaining_rows = list(range(0, points.num_pixels_h))

    LOGGER.info('Starting SpriteMasterclass')
    started = False
    while DISPLAY.loop_running():
        try:
            # Draw
            points.draw()
            status.regen()
            status.draw()
            if len(remaining_rows) == 0:
                started = False

            if started:
                # Update positions
                row = remaining_rows.pop(random.randint(0, len(remaining_rows)-1))
                points.update([row])

            # Parse keypresses
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
