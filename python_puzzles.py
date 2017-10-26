import argparse
import pi3d
import random
import time
from image_randomiser import ImageRandomiser
from status_display import StatusDisplay

from PyQt4 import QtGui
from PyQt4 import QtCore

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run Python Puzzles Masterclass Finalé.')
parser.add_argument("-d", "--demo", action="store_true", help="run in demo mode")
parser.add_argument("-t", "--time", type=int, help="specify the time before restarting demo mode")
args = parser.parse_args()

# Time (seconds) between demo loops
LOOP_TIME  = 10
IMAGE_SIZE = 900
PIXEL_SIZE = 5
BACKGROUND_COLOR = (0.3, 0.3, 0.3, 1.0)

print("""
Space to start/transition
ESC to quit
""")
    
KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log(__name__, level='INFO', file='info.log')

DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=10)
HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

points = ImageRandomiser("MasterclassImage960.png", IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)

def finale_mode():
    try:
        dummy_mode = True
        while dummy_mode:
            # parse teams and requests from server

            # Parse keypresses
            k = KEYBOARD.read()
            if k > -1:
                if k == 27:
                    KEYBOARD.close()
                    break
                if k == 32:
                    dummy_mode = False

        if not dummy_mode:

            status = StatusDisplay(925, -25, CAMERA)
            status.display_list(['team1','team2','team3','team4'])
            
            remaining_rows = list(range(0, points.num_pixels_h))
        
            started = False
            while DISPLAY.loop_running():
            
                if len(remaining_rows) == 0:
                    started = False

                if started:
                    # Update positions
                    row = remaining_rows.pop(random.randint(0, len(remaining_rows)-1))
                    points.update([row])

                # Draw
                points.draw()
                status.regen()
                status.draw()
                
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
                
def demo_mode():
        
    loop_time = LOOP_TIME
    if args.time is not None:
        # Store the specified loop time
        loop_time = args.time
    
    remaining_rows = list(range(0, points.num_pixels_h))
    
    started = False
    while DISPLAY.loop_running():
        try:

            if len(remaining_rows) == 0:
                # wait for the loop time
                time.sleep(loop_time)
                # Reset display
                points.reset()
                LOGGER.info('Reset')
                # Reset row list
                remaining_rows = list(range(0, points.num_pixels_h))
                
            elif started:
                # Update positions
                row = remaining_rows.pop(random.randint(0, len(remaining_rows)-1))
                points.update([row])

            # Draw
            points.draw()

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


if args.demo:
    LOGGER.info('Running in Demo Mode')
    demo_mode()
else:
    LOGGER.info('Running in Finalé Mode')
    finale_mode()
