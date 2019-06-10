import time
import requests
import json
import os
import objectpath
from requests.exceptions import HTTPError

try:
    from daemons.prefab import run
except ModuleNotFoundError:
    print("No module named deamons found, please install it (pip install daemons)")
    sys.exit(1)
except ImportError:
    print("No module named deamons found, please install it (pip install daemons)")
    sys.exit(1)

class DeviceClass:

    def __init__(self, stats):

        self.wired = stats["wired"]
        self.Watts = stats["Wh"]
        self.path  = stats["path"]

class MeterClass:

    def __init__(self, url, paths):
        self.url   = url
        self.paths = paths

    def request(self):

        req = requests.get(self.url)

        try:
            req.raise_for_status()
        except HTTPError as http_err:
            print("HTTP error occurred: {}".format(http_err))
            return None
        except Exception as err:
            print("Error occurred: {}".format(err))
            return None
        else:
            return req

    def retrieve(self, config):
        """
        gather informations from the url gave in the config file
        and keep only want we want from the json returned by the GET
        """
        req = request()

        json_tree = objectpath.Tree(req.json())
        result    = dict()

        for key, query in self.paths.items():

            value = json_tree.execute(query)

            if type(value) is float:
                result[key] = value
            else:
                raise KeyError("Could not find the key {} in the curled json with the query: {}".format(key, query))

        return result

class configClass:

    def __init__(self, path):
        try:
            with open(path, "r") as conf_file:
                dict = json.load(conf_file)
        except Exception as e:
            print("Error occured: {}".format(e))
            pass

        self.devices  = { key:DeviceClass(value) for key, value in dict["devices"].items() }
        self.meter    = MeterClass(dict["meters"]["url"], dict["meters"]["paths"])
        self.interval = dict["interval"]

        self.start_peak    = dict["start peak"]
        self.start_offpeak = dict["start off-peak"]

    def retrieve(self):
        return self.meter.retrieve(self)


class Daemon(run.RunDaemon):
#class Daemon: #Debug

    def do_the_thing(self, config, infos):
        """
        setup of booleans to turn off/on the devices availables
        """
        pass

    def findcwd(self):
        """
        get the cwd from the pidfile path given by the Daemon
        """
        i = len(self.pidfile) - 1

        while self.pidfile[i] != '/':
            i -= 1

        return self.pidfile[0:(i+1)]

    def run(self):

        cwd    = self.findcwd()
        config = configClass(os.path.join(cwd, "config.json"))

        while True:
            data = config.retrieve()
            if data is not None:
                self.do_the_thing(data, config)
            time.sleep(config.interval)

if __name__ == "__main__": #Debug
    d = Daemon()
    d.run()
