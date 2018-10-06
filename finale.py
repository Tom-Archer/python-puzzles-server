import random
import time
from comms import RegistrationRequest, DataResponse

def run(team_manager, incoming_data, outgoing_data, points, status, display, keyboard):
    
    team_list = [team_manager.get_team_name(team) for team in team_manager.get_registered_teams()]
    status.display_list(team_list)

    # wait for teams to time out
    time.sleep(3)
    
    remaining_rows = list(range(0, points.num_pixels_h))

    started = False
    while display.loop_running():
    
        if started:
            
            while not incoming_data.empty():
                # process data received from client
                msg = incoming_data.get()
                
                if type(msg) is RegistrationRequest:
                    # register team
                    team_manager.register(msg.ip_address, msg.team_name)
                    
                elif type(msg) is DataResponse:
                    # deallocate team
                    row_id = team_manager.deallocate(msg.ip_address)
            
                    if row_id != None:
                        # Update positions
                        points.update([row_id])
                   
            # allocate data to free teams
            for team_ip in team_manager.get_free_teams():

                # if there are remaining rows
                if len(remaining_rows) > 0:
                    # get a random remaining row id
                    row_id = remaining_rows.pop(random.randint(0, len(remaining_rows)-1))
                    # get the shuffled data
                    row = points.get_row(row_id)
                    # allocate to the team
                    team_manager.allocate(team_ip, row_id)
                    # put the data on the outgoing queue
                    outgoing_data.put(DataResponse(team_ip, row))
                else:
                    break

            # check timed out teams
            for team_ip in team_manager.get_timed_out_teams():
                team_manager.deallocate(team_ip)
                
        # draw
        points.draw()
        status.regen()
        status.draw()
        
        # parse keypresses
        k = keyboard.read()
        if k > -1:
            if k == 27:
                keyboard.close()
                display.stop()
                break
            elif k == 32:
                started = True
