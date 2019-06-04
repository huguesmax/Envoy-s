import time

try:
    import daemon
except ModuleNotFoundError:
    print("No module named python-deamon found, please install it (pip install python-daemon)")
    sys.exit(1)
except ImportError:
    print("No module named python-deamon found, please install it (pip install python-daemon)")
    sys.exit(1)

def retrieve():
    """
    gather informations and keep only want we want
    """
    pass



def run():
    with daemon.DaemonContext():
        infos = retrieve()

if __name__ == "__main__":
    run()
