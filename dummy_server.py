import curses
import datetime
import lists
from comms import RegistrationRequest, DataResponse

RECENT = 12
LIST_LENGTH = 100

def format_timestamp():
    return '{:%H:%M:%S} '.format(datetime.datetime.now())

def format_name_ip(team_name, ip_address):
    return ("\'" + team_name + "\' " if team_name is not None else "") + "(" + str(ip_address) + ") "

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

def run(team_manager, data_display, incoming_data, outgoing_data, keyboard):
    screen = keyboard.key
    draw_curses_menu(screen)
    screen.refresh()    

    while True:
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
        k = keyboard.read()
        if k > -1:
            if k == 27:
                keyboard.close()
                return False
            else:
                return True
