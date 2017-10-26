import argparse

parser = argparse.ArgumentParser(description='Run Python Puzzles Masterclass Finalé.')
parser.add_argument("-d", "--demo", action="store_true", help="run in demo mode")
parser.add_argument("-t", "--time", type=int, help="specify the time before restarting demo mode")
args = parser.parse_args()

# Time (seconds) between demo loops
loop_time = 10

if args.demo:
    print("Run in demo mode")
    if args.time is not None:
        # Store the specified loop time
        loop_time = args.time
else:
    print("Run in single-mode")
