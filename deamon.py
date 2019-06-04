import time
import json
from collections import Iterable

try:
    import daemon
except ModuleNotFoundError:
    print("No module named python-deamon found, please install it with python 2.7 (pip install python-daemon)")
    sys.exit(1)
except ImportError:
    print("No module named python-deamon found, please install it with python 2.7 (pip install python-daemon)")
    sys.exit(1)

HTTP_ERRORS    = [400, 401, 402, 403, 404, 500]
VALUES_TO_FIND = []

def __find_dict(x, iterable):
    """
    find a value in a stupid herierachical json dict of list of dict of list of...
    """

    for elt in iterable:
        if !(isinstance(elt, Iterable)):
            if elt == x:
                return iterable[x] # I know this is a dictionnary cause of json structure
        else:
            value = __find_dict(x, elt)

            if value != None:
                return value

    return None

def retrieve():
    """
    gather informations and keep only want we want
    """
    req = requests.get('http://envoy.local/production.json')

    if req.status_code in HTTP_ERRORS:
        raise Exception("http error: " + req.status_code)

    req = req.json().dump()

    result = dict()

    for x in VALUES_TO_FIND:
        value = __find_dict(x, req)

        if value != None:
            result[x] = value
        else
            raise KeyError("Could not find the given key in the json: " + x)

    return result


def run():
    with daemon.DaemonContext():
        infos = retrieve()

if __name__ == "__main__":
    run()
