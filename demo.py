import random
import time

LOOP_TIME  = 10

def run(loop_time, points, display, keyboard):
        
    if loop_time is None:
        # Use the default time
        loop_time = LOOP_TIME

    remaining_rows = list(range(0, points.num_pixels_h))
    
    started = False
    while display.loop_running():
        
        if len(remaining_rows) == 0:
            # wait for the loop time
            time.sleep(loop_time)
            # Reset display
            points.reset()
            # Reset row list
            remaining_rows = list(range(0, points.num_pixels_h))
            
        elif started:
            # Update positions
            row = remaining_rows.pop(random.randint(0, len(remaining_rows)-1))
            points.update([row])

        # Draw
        points.draw()

        # Parse keypresses
        k = keyboard.read()
        if k > -1:
            if k == 27:
                keyboard.close()
                keyboard.stop()
                break
            if k == 32:
                started = True

