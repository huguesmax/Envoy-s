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

class Daemon(run.RunDaemon):
#class Daemon: #Debug

    def retrieve(self, config):
        """
        gather informations from the url gave in the config file
        and keep only want we want from the json returned by the GET
        """

        req = requests.get(config["meters"]["url"])

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

        for key, query in config["meters"]["paths"].items():

            value = json_tree.execute(query)

            if type(value) is float:
                result[key] = value
            else:
                raise KeyError("Could not find the key '{}' in the curled json with the query: {}".format(key, query))

        return result


    def run(self):
        with open("config.json", "r") as conffile:
            config = json.load(conffile)
        while True:
            infos = self.retrieve(config)
            if infos is not None:
                #do the thing
            time.sleep(config["interval"])

if __name__ == "__main__": #Debug
    d = Daemon()
    d.run()
