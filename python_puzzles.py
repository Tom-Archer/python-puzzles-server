import argparse
import pi3d
import time
from image_randomiser import ImageRandomiser
#from status_display import StatusDisplay

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

def finale_mode():
    dummy_mode = True
    while dummy_mode:
        # parse teams and requests from server
        
        # Parse keypresses
        k = KEYBOARD.read()
        if k > -1:
            if k == 27:
                break
            if k == 32:
                dummy_mode = False

    if not dummy_mode:
        DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=20)
        HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
        CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

        points = ImageRandomiser("MasterclassImage960.png", IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)
        #status = StatusDisplay(CAMERA)
        
        remaining_rows = list(range(0, points.num_pixels_h))
    
        started = False
        while DISPLAY.loop_running():
            try:
                # Draw
                points.draw()

                if len(remaining_rows) == 0:
                    self.started = False

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
                
def demo_mode():
    
    DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=20)
    HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
    CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

    points = ImageRandomiser("MasterclassImage960.png", IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)
    #status = StatusDisplay(CAMERA)
    
    loop_time = LOOP_TIME
    if args.time is not None:
        # Store the specified loop time
        loop_time = args.time
    
    remaining_rows = list(range(0, points.num_pixels_h))
    
    started = False
    while DISPLAY.loop_running():
        try:
            # Draw
            points.draw()

            if len(remaining_rows) == 0:
                # wait for the loop time
                time.sleep(loop_time)
                # reset display
                points.reset()
                remaining_rows = list(range(0, points.num_pixels_h))
                
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

# separate display loops for demo-mode and finale mode
# processing loop for dummy-mode
if args.demo:
    LOGGER.info('Running in Demo Mode')
    demo_mode()
   
else:
    LOGGER.info('Running in Finalé Mode')
    finale_mode()
