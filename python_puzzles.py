import argparse
import curses
import pi3d
import random
import time
from image_randomiser import ImageRandomiser
from status_display import StatusDisplay

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
    
KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log(__name__, level='INFO', file='info.log')

DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=10)
HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

points = ImageRandomiser("MasterclassImage960.png", IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)

def finale_mode(screen):
    try:
        dummy_mode = True
        while dummy_mode:

            # parse teams and requests from server
            data = ["22:04:22 - data received from team 1 (192.168.0.2) is sorted",
                    "22:04:47 - data received from team 2 (192.168.0.3) is NOT sorted",
                    "22:04:53 - data received from team 3 (192.168.0.4) is sorted"]
            draw_curses_data(screen, data) 
            screen.refresh()    

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

def draw_curses_menu(screen):
    screen.border(0)
    screen.addstr(2, 2, "Dummy server is currently running.")
    screen.addstr(4, 2, "Please select an option...")
    screen.addstr(6, 4, "ESC   - Exit")
    screen.addstr(7, 4, "SPACE - Start finalé")

    screen.move(9, 0)
    screen.addch(curses.ACS_LTEE)
    height, width = screen.getmaxyx()
    screen.hline(curses.ACS_HLINE, width)
    screen.move(9, width-1)
    screen.addch(curses.ACS_RTEE)

def draw_curses_data(screen, data):
    # Clear previous rows
    height, width = screen.getmaxyx()
    for i in range(11, 21):
        if i < height-2:
            screen.move(i, 2)
            screen.hline(" ", width-3)    

    # Show new rows
    i=11
    for data_line in data:
        if i < height-2:
            screen.addstr(i, 2, data_line)
            if len(data_line) > width-2:
                i = i + 2
            else:
                i = i + 1
         
if args.demo:
    LOGGER.info('Running in Demo Mode')
    demo_mode()
else:
    screen = KEYBOARD.key
    draw_curses_menu(screen)
    screen.refresh()    
    
    LOGGER.info('Running in Finalé Mode')
    finale_mode(screen)
