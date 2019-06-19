import time
import logging
import requests
import json
import os
import objectpath
from requests.exceptions import HTTPError
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from daemons.prefab import run

LOG = simple_startstop.LOG

class Device:
    """
    The virtual class Device is the base of was will be litten

    it setups:
        * timelit:     time the device has been litten this day in seconds
        * Watts:       the consumption of the device
        * time_to_lit: the time this device should be light this day
    """


    def __init__(self, stats, ttl):
        """construtor of Device class:
            :params stats: dict which come from the config.json
            :params ttl:   the time_to_lit the device this day
        """
        self.Watts   = stats["Wh"]
        self.change_day(ttl)

    def change_day(self, ttl):
        """used to reset the @timelit and set a new value to @time_to_lit"""
        self.timelit = 0
        self.time_to_lit = ttl

    def IsEnoughLitten(self):
        return timelit >= time_to_lit

class Gpio:
    """
    The abstract class Gpio uses gpiozero to switch a remote gpio on IP
    It only sets the self.gpio value when the host value in the config.json is not empty and the pin number is not -1
    """

    def __init__(self, stats):

        if "gpio" in stats and stats["gpio"]["host"] != "" and stats["gpio"]["pin"] != -1:
            factory   = PiGPIOFactory(host=stats["gpio"]["host"])
            self.gpio = LED(stats["gpio"]["pin"], pin_factory=factory)
        else:
            LOG.error("error occured in Gpio.__init__: cannot initialize the gpio attribute")
            self.gpio = None

    def count(self, interval):
        """used to increment the timelit data of the device only if the gpio is lit and if the gpio exist"""
        if self.gpio != None and self.gpio.is_lit:
            self.timelit += interval

class PoolPump(Device, Gpio):
    """
    A class dedicated to the the pool pump and which inherit from Device and Gpio
    """
    def __init__(self, stats, ttl):

        Device.__init__(self, stats, ttl)
        Gpio.__init__(self, stats)


class HTTP:

    def _get(self, url, login=None, header=None):
        """GET request:
            :param url:    the destination
            :param login:  a user and a password as a tuple like this ('user', 'pwd')
            :param header: a header for the request as a dictionnary
            :type url:     string
            :type login:  tuple<string, string>
            :type header: dict<string, string>
            :typ
        """
        if auth is None and headers is None:
            req = requests.get(url)
        elif headers is None:
            req = requests.get(url, auth=login)
        elif auth is None:
            req = requests.get(url, headers=header)
        else:
            req = requests.get(url, headers=header, auth=login)

        try:
            req.raise_for_status()
        except HTTPError as http_err:
            LOG.error("HTTP error occurred: {}".format(http_err))
            return None
        except Exception as err:
            LOG.error("Error occurred in HTTP._get: {}".format(err))
            return None
        else:
            return req.json()

    def _post(self, url, post, login=None, header=None):
        """POST request:
            @url:    destination
            @post:   the data to POST
            @login:  a user and a password as a tuple like this ('user', 'pwd')
            @header: a header for the request as a dictionnary
        """
        if auth is None and headers is None:
            req = requests.post(url, data=post)
        elif headers is None:
            req = requests.get(url, data=post, auth=login)
        elif auth is None:
            req = requests.get(url, data=post, headers=header)
        else:
            req = requests.get(url, data=post, headers=header, auth=login)

        try:
            req.raise_for_status()
        except HTTPError as http_err:
            LOG.error("HTTP error occurred: {}".format(http_err))
            return None
        except Exception as err:
            LOG.error("Error occurred in HTTP._get: {}".format(err))
            return None
        else:
            return req.json()


class MeterClass(HTTP):
    """
    The MeterClass permit to retrieve datas from the differents data sources on the web using HTTP requests
    """
    def __init__(self, stats):
        self.url   = stats["url"]
        self.paths = stats["paths"]

    def retrieve(self):
        """
        gather informations from the url gave in the config file
        and keep only want we want from the json returned by the GET
        """
        data = self._get(self.url)

        if data is None:
            LOG.error("error occured in MeterClass.retrieve: get request failed")
            return data

        json_tree = objectpath.Tree(data)
        result    = dict()

        for key, query in self.paths.items():

            value = json_tree.execute(query)

            if type(value) is float:
                result[key] = value
            else:
                LOG.error("Could not find the key {} in the curled json with the query: {}".format(key, query))

        return result

class Material:

    def __init__(self, path):
        try:
            with open(path, "r") as f:
                s = f.read()
                s = s.replace('\t','')
                s = s.replace('\n','')
                s = s.replace(',}','}')
                s = s.replace(',]',']')
                data = json.loads(s)
        except Exception as e:
            LOG.error("Error occured in Material.__init__: {}".format(e))
            pass

        self.start_peak    = data["start peak hour"]
        self.peak_price    = data["peak price"]
        self.start_offpeak = data["start off-peak hour"]
        self.offpeak_price = data["offpeak price"]

        self.panels   = MeterClass(data["meters"]["panels"])
        self.weather  = MeterClass(data["meters"]["weather"])
        self.interval = data["interval"]
        self.devices  = dict()

        weather = self.weather_retrieve()
        #the pool pump should be lit for the half of the temperature outside as hours, which give this formula
        ttl = int(weather["temp"] - 273) // 2 * 3600

        #here is the manual part to modify to change the behaviour of this script

        if data["devices"]["pool_pump"]["wired"]:
            devices["pool_pump"] = PoolPump(data["devices"]["pool_pump"], ttl)

        if data["devices"]["VW_E-Golf"]["wired"]:
            devices["VW_E-Golf"] = None # can't create what a don't know

    def energy_retrieve(self):
        return self.panels.retrieve()

    def weather_retrieve(self):
        return self.weather.retrieve() #this temp data is in kelvin

    def count(self):
        for dev in devices.values():
            dev.count(self.interval)

    def change_day(self):
        for dev in devices.values():
            dev.change_day()


class Daemon(run.RunDaemon):
#class Daemon: #Debug

    def setvalues(self, config):
        """
        appeled when starting the daemons
        """
        pass

        self.devices_on  = 0
        self.devices_off = 0


    def do_the_thing(self, material):
        """
        setup of booleans to turn off/on the devices availables
        """
        pass

        data = material.energy_retrieve()


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
        mat = Material(os.path.join(cwd, "config.json"))

        setvalues(mat)

        while True:
            self.do_the_thing(mat)
            time.sleep(mat.interval)
            mat.count()

if __name__ == "__main__": #Debug
    d = Daemon()
    d.run()
