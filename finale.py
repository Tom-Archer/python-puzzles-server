import random

def run(team_manager, incoming_data, outgoing_data, points, status, display, keyboard):
    
    team_list = [team_manager.get_team_name(team) for team in team_manager.get_registered_teams()]
    status.display_list(team_list)

    # To be finished.
    # do we want to wait for all teams to have timed out?
    
    remaining_rows = list(range(0, points.num_pixels_h))

    started = False
    while display.loop_running():
    
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
        k = keyboard.read()
        if k > -1:
            if k == 27:
                keyboard.close()
                display.stop()
                break
            if k == 32:
                started = True
