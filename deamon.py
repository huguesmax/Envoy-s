import time
import requests
import json
import objectpath
from requests.exceptions import HTTPError

try:
    from daemons.prefab import run
except ModuleNotFoundError:
    print("No module named python-deamon found, please install it (pip install daemons)")
    sys.exit(1)
except ImportError:
    print("No module named python-deamon found, please install it (pip install daemons)")
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

    def retrieve(self, config):
        """
        gather informations from the url gave in the config file
        and keep only want we want from the json returned by the GET
        """

        req = requests.get(self.url)

        try:
            req.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return None
        except Exception as err:
            print(f'Error occurred: {err}')
            return None

        json_tree = objectpath.Tree(req.json())
        result    = dict()

        for key, query in self.paths.items():

            value = json_tree.execute(query)

            if type(value) is float:
                result[key] = value
            else:
                raise KeyError(f"Could not find the key '{key}' in the curled json with the query: {query}")

        return result

class configClass:

    def __init__(self):
        with open("config.json", "r") as conf_file:
            dict = json.load(conf_file)

        self.devices  = { key:DeviceClass(value) for key, value in dict["devices"].items() }
        self.meter    = MeterClass(dict["meters"]["url"], dict["meters"]["paths"])
        self.interval = dict["interval"]

        self.start_peak    = dict["start peak"]
        self.start_offpeak = dict["start off-peak"]


class Daemon(run.RunDaemon):
#class Daemon: #Debug

    def do_the_thing(config, infos):
        """
        setup of booleans to turn off/on the devices availables
        """
        pass

    def run(self):
        config = configClass()
        while True:
            data = config.meter.retrieve(config)
            if infos is not None:
                do_the_thing(data, config)
            time.sleep(config.interval)

if __name__ == "__main__": #Debug
    d = Daemon()
    d.run()
