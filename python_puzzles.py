import argparse
import curses
import pi3d
import random
import time
import collections
import datetime
import lists
import ipaddress

from comms import RegistrationRequest, DataResponse
from image_randomiser import ImageRandomiser
from multiprocessing import Queue
from status_display import StatusDisplay
from team_manager import TeamManager

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run Python Puzzles Masterclass Finalé.')
parser.add_argument("-d", "--demo", action="store_true", help="run in demo mode")
parser.add_argument("-t", "--time", type=int, help="specify the time before restarting demo mode")
args = parser.parse_args()

# Dummy Server
RECENT = 12
LIST_LENGTH = 100

# Time (seconds) between demo loops
LOOP_TIME  = 10

# Pi3D setup
IMAGE_SIZE = 900
PIXEL_SIZE = 5
BACKGROUND_COLOR = (0.3, 0.3, 0.3, 1.0)
    
KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log(__name__, level='INFO', file='info.log')

DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=10)
HWIDTH, HHEIGHT = int(DISPLAY.width / 2.0), int(DISPLAY.height / 2.0)
CAMERA = pi3d.Camera(at=(HWIDTH,-HHEIGHT,0), eye=(HWIDTH,-HHEIGHT,-0.1), is_3d=False)

points = ImageRandomiser("MasterclassImage960.png", IMAGE_SIZE, IMAGE_SIZE, PIXEL_SIZE, CAMERA)

def format_timestamp():
    return '{:%H:%M:%S} '.format(datetime.datetime.now())

def format_name_ip(team_name, ip_address):
    return ("\'" + team_name + "\' " if team_name is not None else "") + "(" + str(ip_address) + ") "

def finale_mode(screen):

    team_manager = TeamManager()
    data_display = collections.deque(maxlen = RECENT)
    incoming_data = Queue()
    outgoing_data = Queue()

    # for testing add some dummy data
    incoming_data.put(RegistrationRequest(ipaddress.ip_address('192.0.2.2'), "team 1"))
    incoming_data.put(RegistrationRequest(ipaddress.ip_address('192.0.2.3'), "team 2"))
    incoming_data.put(RegistrationRequest(ipaddress.ip_address('192.0.2.4'), "a very long team name"))
    incoming_data.put(DataResponse(ipaddress.ip_address('192.0.2.2'), lists.get_list(LIST_LENGTH)))
    incoming_data.put(DataResponse(ipaddress.ip_address('192.0.2.3'), sorted(lists.get_list(LIST_LENGTH))))
    incoming_data.put(DataResponse(ipaddress.ip_address('192.0.2.4'), lists.get_list(LIST_LENGTH)))
            
    try:
        dummy_mode = True
        while dummy_mode:

            while not incoming_data.empty():
                # process data received from client
                msg = incoming_data.get()

                if type(msg) is RegistrationRequest:
                    #register team
                    team_manager.register(msg.ip_address, msg.team_name)
                    
                elif type(msg) is DataResponse:
                    # deallocate team
                    team_manager.deallocate(msg.ip_address)
                    
                    # check whether data is sorted
                    list_sorted = False
                    
                    if isinstance(msg.data, list) and sorted(msg.data) == msg.data:
                        list_sorted = True

                    # add to data_display
                    team_name = team_manager.get_team_name(msg.ip_address)
                    data_display.append(format_timestamp() + "Data from " +
                                        format_name_ip(team_name, msg.ip_address) +
                                        "is " + ("" if list_sorted else "NOT ") + "sorted")    
                    
            # allocate data to free teams
            for team_ip in team_manager.get_free_teams():
                team_manager.allocate(team_ip, lists.get_list(LIST_LENGTH))
                outgoing_data.put(DataResponse(team_ip, lists.get_list(LIST_LENGTH)))

                # add to data display
                team_name = team_manager.get_team_name(team_ip)
                data_display.append(format_timestamp() + "Sent data to " +
                                    format_name_ip(team_name, team_ip))

            # check timed out teams
            for team_ip in team_manager.get_timed_out_teams():
                team_manager.deallocate(team_ip)
                
                # add to data display
                team_name = team_manager.get_team_name(team_ip)
                data_display.append(format_timestamp() + "Response from "+
                                    format_name_ip(team_name, team_ip) +
                                    "timed out ")
                
            draw_curses_data(screen, data_display) 
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

            team_list = map(team_manager.get_team_name, team_manager.get_registered_teams())
            
            status.display_list(team_list)

            # do we want to wait for all teams to have timed out?
            
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
    for i in range(11, 11+RECENT):
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
