import logging
import os
import sys
import time

from daemon import Daemon


if __name__ == '__main__':

    action = sys.argv[1]
    logfile = os.path.join(os.getcwd(), "sleepy.log")
    pidfile = os.path.join(os.getcwd(), "sleepy.pid")

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    d = Daemon(pidfile=pidfile)

    if action == "start":

        d.start()

    elif action == "stop":

        d.stop()

    elif action == "restart":

        d.restart()

    else:
        print("please select between start and stop to manage the daemon")
