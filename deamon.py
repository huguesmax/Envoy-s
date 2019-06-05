import time
import requests
import json
import objectpath
from requests.exceptions import HTTPError

try: from daemons.prefab import run
except ModuleNotFoundError:
    print("No module named python-deamon found, please install it (pip install daemons)")
    sys.exit(1)
except ImportError:
    print("No module named python-deamon found, please install it (pip install daemons)")
    sys.exit(1)

class Daemon(run.RunDaemon):
#class Daemon: #Debug

    INTERVAL       = 30
    HTTP_ERRORS    = [400, 401, 402, 403, 404, 500]
    VALUES_TO_FIND = ["measurementType"]

    def retrieve(self):
        """
        gather informations and keep only want we want
        """

        req = requests.get('http://envoy.local/production.json')

        try:
            # If the response was successful, no Exception will be raised
            req.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            pass
        except Exception as err:
            print(f'Error occurred: {err}')
            pass

        json_tree = objectpath.Tree(req.json())

        result = dict()

        for x in self.VALUES_TO_FIND:
            values = tuple(json_tree.execute('$..{}'.format(x)))

            if len(values) > 0:
                result[x] = values[0]
            else:
                raise KeyError("Could not find the key '{}' in the json".format(x))

        return result


    def run(self):
        while True:
            infos = self.retrieve()
            if infos is not None:
                #do the thing
            time.sleep(self.INTERVAL)

if __name__ == "__main__": #Debug
    d = Daemon()
    d.run()
