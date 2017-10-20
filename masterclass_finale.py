#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' PyQt window containing Masterclass finalé.
'''

import sys
import pi3d
import numpy as np
import random
from PyQt4 import QtGui
from PyQt4 import QtCore
from PIL import Image
from image_randomiser import ImageRandomiser

W, H = 900, 900
FPS = 20
PIXEL_SIZE = 5

class QtWindow(QtGui.QWidget):

  def __init__(self, width, height, pixel_size, texture_path, fps=20):
    super(QtWindow, self).__init__()
    ''' layer set to -128 to hide behind X desktop
    '''
    self.DISPLAY = pi3d.Display.create(w=width, h=height, frames_per_second=fps, layer=-128)

    HWIDTH, HHEIGHT = int(self.DISPLAY.width / 2.0), int(self.DISPLAY.height / 2.0)
    CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

    self.points = ImageRandomiser(texture_path, width, height, pixel_size, CAMERA)
    self.started = False
    self.remaining_rows = list(range(0, self.points.num_pixels_h))
    self.initUI()
      
  def initUI(self):
    button1 = QtGui.QPushButton('Start')
    button1.clicked.connect(self.start)
    button2 = QtGui.QPushButton('Close')
    button2.clicked.connect(self.close)

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(button1)
    vbox.addWidget(button2)
    vbox.addStretch(1)

    # Setup display
    self.img = QtGui.QLabel('image')
    a = np.zeros((self.DISPLAY.width, self.DISPLAY.height, 4), dtype=np.uint8)
    im = QtGui.QImage(a, self.DISPLAY.width, self.DISPLAY.height, QtGui.QImage.Format_RGB888)
    self.img.setPixmap(QtGui.QPixmap.fromImage(im))
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(self.img)
    hbox.addLayout(vbox)
    hbox.addStretch(1)
    self.setLayout(hbox)

    self.setWindowTitle('Python Puzzles!')
    self.show()
    
  def pi3d_loop(self):
    self.DISPLAY.loop_running()
    self.points.draw()

    if len(self.remaining_rows) == 0:
        self.started = False
        
    if self.started:
        # Update positions
        row = self.remaining_rows.pop(random.randint(0, len(self.remaining_rows)-1))
        self.points.update([row])

    # This creates a series of still images in the QtWindow
    # The frame rate as a result will be lower
    im = QtGui.QImage(pi3d.screenshot(), self.DISPLAY.width, self.DISPLAY.height, QtGui.QImage.Format_RGB888)
    self.img.setPixmap(QtGui.QPixmap.fromImage(im))
        
  def start(self):
    self.started = True
    

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = QtWindow(W, H, PIXEL_SIZE, "MasterclassImage960.png")

    timer = QtCore.QTimer()
    timer.timeout.connect(win.pi3d_loop)
    msfps = int(1000/FPS) # FPS in milliseconds
    timer.start(msfps)
    # The loop handles the updates AND sorting
    #    Setup the timer internally
    #    Move the sorting to an external thread
    #    Only draw when necessary

    sys.exit(app.exec_())
    



