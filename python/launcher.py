import logging
import os
import sys
import time
import daemon


if __name__ == '__main__':

    help = "please select between those actions: \n\n -start: launch the daemon \n -stop: stop it \n -restart: restart it \n -pause: stop all devices but doesn't stop the daemon until play \n -play: returning the daemon to his normal behaviour after a pause \n"

    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        action = None
        
    logfile = os.path.join(os.getcwd(), "daemon.log")
    pidfile = os.path.join(os.getcwd(), "daemon.pid")

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    d = daemon.Daemon(pidfile=pidfile)

    if action == "start":

        d.start()

    elif action == "stop":

        d.stop()

    elif action == "restart":

        d.restart()

    elif action == "pause":

        d.pause()

    elif action == "play":

        d.play()

    else:
        print(help)
