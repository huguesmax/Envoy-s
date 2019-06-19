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

    def __init__(self, stats, ttl):

        self.timelit = 0
        self.wired   = stats["wired"]
        self.Watts   = stats["Wh"]
        self.change_day(ttl)

    def change_day(self, ttl):
        self.timelit = 0
        self.time_to_lit = ttl

    def IsEnoughLitten(self):
        return timelit >= time_to_lit

class Gpio:

    def __init__(self, stats):

        if "gpio" in stats and stats["gpio"]["host"] != "" and stats["gpio"]["pin"] != -1:
            factory   = PiGPIOFactory(host=stats["gpio"]["host"])
            self.gpio = LED(stats["gpio"]["pin"], pin_factory=factory)
        else
            self.gpio = None

    def count(self, interval):
        if self.wired and self.gpio and self.gpio.is_lit:
            self.timelit += interval

class PoolPump(Device, Gpio):

    def __init__(self, stats, ttl):

        Device.__init__(self, stats, ttl)
        Gpio.__init__(self, stats)


class MeterClass:

    def __init__(self, stats):
        self.url   = stats["url"]
        self.paths = stats["paths"]

    def __request(self):

        req = requests.get(url)

        try:
            req.raise_for_status()
        except HTTPError as http_err:
            LOG.error("HTTP error occurred: {}".format(http_err))
            return None
        except Exception as err:
            LOG.error("Error occurred in MeterClass.request: {}".format(err))
            return None
        else:
            return req

    def retrieve(self):
        """
        gather informations from the url gave in the config file
        and keep only want we want from the json returned by the GET
        """
        req = self.__request()

        if req is None:
            return req

        json_tree = objectpath.Tree(req.json())
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
                dict = json.loads(s)
        except Exception as e:
            LOG.error("Error occured in Material.__init__: {}".format(e))
            pass

        self.start_peak    = dict["start peak hour"]
        self.peak_price    = dict["peak price"]
        self.start_offpeak = dict["start off-peak hour"]
        self.offpeak_price = dict["offpeak price"]

        self.panels   = MeterClass(dict["meters"]["panels"])
        self.weather  = MeterClass(dict["meters"]["weather"])
        self.interval = dict["interval"]
        self.devices  = dict()

        weather = self.weather.retrieve()

        #the pool pump should be lit for the half of the temperature outside as hours, which give this formula
        ttl = int(weather["temp"] - 273) // 2 * 3600

        devices["pool_pump"] = PoolPump(dict["devices"]["pool_pump"], ttl)
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

        self.deviceslit = 0
        self.


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
