import argparse
import collections
import demo
import dummy_server
import finale
import pi3d
#from comms import Server
from image_randomiser import ImageRandomiser
from multiprocessing import Queue
from status_display import StatusDisplay
from team_manager import TeamManager

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run Python Puzzles Masterclass Finalé.')
parser.add_argument("-d", "--demo", action="store_true", help="run in demo mode")
parser.add_argument("-t", "--time", type=int, help="specify the time before restarting demo mode")
args = parser.parse_args()

# Pi3D setup
IMAGE_NAME = "MasterclassImage960.png"
IMAGE_SIZE = 900
PIXEL_SIZE = 5
BACKGROUND_COLOR = (0.3, 0.3, 0.3, 1.0)
    
KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log(__name__, level='INFO', file='info.log')

DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=10)
HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

def finale_mode():

    team_manager = TeamManager()
    data_display = collections.deque(maxlen = dummy_server.RECENT)
    incoming_data = Queue()
    outgoing_data = Queue()
    # To do: set up comms/server here
    
    try:
        if dummy_server.run(team_manager, data_display, incoming_data, outgoing_data, KEYBOARD):

            points = ImageRandomiser(IMAGE_NAME, IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)
            status = StatusDisplay(925, -25, CAMERA)

            finale.run(team_manager, incoming_data, outgoing_data, points, status, DISPLAY, KEYBOARD)

    except Exception as e:
        KEYBOARD.close()
        DISPLAY.stop()
        LOGGER.info(str(e))    

def demo_mode():
    try:
        points = ImageRandomiser(IMAGE_NAME, IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)
        
        demo.run(args.time, points, DISPLAY, KEYBOARD)
        
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
