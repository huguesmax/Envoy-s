import logging
import os
import sys
import time
import daemon


if __name__ == '__main__':

    action = sys.argv[1]
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

    else:
        print("please select between start, stop and restart to manage the daemon")
