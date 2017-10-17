#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Sprites rendered using a diy points class and special shader uv_spriterot.

This demo builds on the SpriteBalls demo but adds sprite image rotation, thanks
to Joel Murphy on stackoverflow. The information is used by the uv_spritemult
shader as follows

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
sampling in this case each sprite has a patch 0.125x0.125 as there
are 8x8 on the sheet. However unif[48] is set to 0.1 to leave a margin of
0.0125 around each sprite.

The movement of the vertices is calculated using numpy which makes it very
fast but it is quite hard to understand as all the iteration is done
automatically.
"""
print("""
ESC to quit
""")
import numpy as np
import random

#import demo
import pi3d


IMAGE_SIZE = 900
PIXEL_SIZE = 5

num_pixels = int(IMAGE_SIZE / PIXEL_SIZE)
point_size = 1.0 * float(PIXEL_SIZE / 960)

KEYBOARD = pi3d.Keyboard()
#LOGGER = pi3d.Log.logger(__name__)

BACKGROUND_COLOR = (0.3, 0.3, 0.3, 1.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=20)
HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)

CAMERA = pi3d.Camera(is_3d=False)
shader = pi3d.Shader("uv_pointsprite")

img = pi3d.Texture("MasterclassImage960.png", mipmap=False, i_format=pi3d.GL_RGBA, filter=pi3d.GL_NEAREST)
# i_format=pi3d.GL_LUMINANCE_ALPHA ## see what happens with a converted texture type
loc = np.zeros((num_pixels*num_pixels, 3))
uv = np.zeros((num_pixels*num_pixels, 2)) # u picnum.u v
#uv[:,:] = 0.0 # all start off same. uv is top left corner of square

for j in range(0, num_pixels):
 for i in range(0, num_pixels):
    loc[i+j*num_pixels,0] = -HWIDTH + (i * PIXEL_SIZE) + PIXEL_SIZE/2
    loc[i+j*num_pixels,1] = HHEIGHT - (j * PIXEL_SIZE) - PIXEL_SIZE/2
    loc[i+j*num_pixels,2] = 0.999 # no scaling

    uv[i+j*num_pixels,0] = i * point_size  # all start off same. uv is top left corner of square
    uv[i+j*num_pixels,1] = j * point_size

# leave this alone
rot = np.zeros((num_pixels*num_pixels, 3)) # :,0 for rotation
rot[:,1] = 999.999 # :,1 R, G
rot[:,2] = 999.999 # :,2 B, A

bugs = pi3d.Points(camera=CAMERA, vertices=loc, normals=rot, tex_coords=uv,
                   point_size=PIXEL_SIZE)
bugs.set_draw_details(shader, [img])
bugs.unif[48] = point_size

while DISPLAY.loop_running():
  # update positions

  # draw
  bugs.draw()

  k = KEYBOARD.read()
  if k > -1:
    if k == 27:
      KEYBOARD.close()
      DISPLAY.stop()
      break


