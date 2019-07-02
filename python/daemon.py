import time
import logging
import requests
import json
import os
import objectpath
import datetime
from enum import Enum
from requests.exceptions import HTTPError
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from daemons.prefab import step

logging.basicConfig(filename="daemon.log", level=logging.DEBUG)

class Device:
    """
    The virtual class Device is the base of was will be litten

    it setups:
        * timelit:     time the device has been litten this day in seconds
        * Watts:       the consumption of the device
        * time_to_lit: the time this device should be light this day
    """


    def __init__(self, watts, ttl):
        """construtor of Device class:
            :params watts: dict which come from the config.json
            :params ttl:   the time_to_lit the device this day
            :type watts:   int
            :type ttl:     int
        """
        self.Watts   = watts
        self.change_day(ttl)

    def change_day(self, ttl):
        """used to reset the @timelit and set a new value to @time_to_lit"""
        logging.info("the device named {} will be light {} hours this day".format(self, ttl // 3600))
        self.timelit = 0
        self.time_to_lit = ttl

    def IsEnoughLitten(self):
        return self.timelit >= self.time_to_lit

class Gpio:
    """
    The abstract class Gpio uses gpiozero to switch a remote gpio on IP
    It only sets the self.gpio value when the host value in the config.json is not empty and the pin number is not -1
    """

    def __init__(self, ip, pin):
        """
        Construtor of the class Gpio:
            :param ip:  the http address of the raspberry pi
            :param pin: the pin number to lit
            :type ip:   string
            :type pin:  int
        """
        if ip != "" and pin != -1:
            factory   = PiGPIOFactory(host=ip)
            self.gpio = LED(pin, pin_factory=factory)
        else:
            logging.error("error occured in Gpio.__init__: cannot initialize the gpio attribute")
            self.gpio = None

    def count(self, interval):
        """used to increment the timelit data of the device only if the gpio is lit and if the gpio exist"""
        if self.gpio != None and self.gpio.is_lit:
            logging.info("the device named {} is lit so added {} secondes to his time litted".format(self, interval))
            self.timelit += interval

class PoolPump(Device, Gpio):
    """
    A class dedicated to the the pool pump and which inherit from Device and Gpio
    """
    def __init__(self, stats, ttl):

        Device.__init__(self, stats["Wh"], ttl)
        Gpio.__init__(self, stats["gpio"]["host"], stats["gpio"]["pin"])

    def __repr__(self):
        return "Pool pump"

class HTTP:

    def __try_errors(self, req):
        """
        just here to find if there is an error in the request
        """
        try:
            req.raise_for_status()
        except HTTPError as http_err:
            logging.error("HTTP error occurred: {}".format(http_err))
            return None
        except Exception as err:
            logging.error("Error occurred in HTTP._get: {}".format(err))
            return None
        else:
            return req

    def _get(self, url, login=None, header=None):
        """GET request:
            :param url:    the destination
            :param login:  a user and a password as a tuple like this ('user', 'pwd')
            :param header: a header for the request as a dictionnary
            :type url:     string
            :type login:   tuple
            :type header:  dict
            :return:       the json response of the GET
            :rtype:        dict
        """
        if login is None and header is None:
            req = requests.get(url)
        elif header is None:
            req = requests.get(url, auth=login)
        elif login is None:
            req = requests.get(url, headers=header)
        else:
            req = requests.get(url, headers=header, auth=login)

        return self.__try_errors(req).json()

    def _post(self, url, post, login=None, header=None):
        """POST request:
            :param url:    the destination
            :param post:   the data to post
            :param login:  a user and a password as a tuple like this ('user', 'pwd'), it is optional
            :param header: a header for the request as a dictionnary, it is optional
            :type url:     string
            :type post:    dict
            :type login:   tuple
            :type header:  dict
            :return:       the json response of the POST
            :rtype:        dict
        """
        if login is None and header is None:
            req = requests.post(url, data=post)
        elif header is None:
            req = requests.post(url, data=post, auth=login)
        elif login is None:
            req = requests.post(url, data=post, headers=header)
        else:
            req = requests.post(url, data=post, headers=header, auth=login)

        return self.__try_errors(req).json()

class VW_EGolf(Device, HTTP):
    pass
    """
    the main class for the Golf charge device              /!\ actually unable to work
    """

    BASE  = "http://{h}/r?rapi=%24"
    Cmd   = Enum("Cmd", "sleep reset enable disable")

    __CmdToUrl = {
        Cmd.sleep:   "FS",
        Cmd.reset:   "FR",
        Cmd.enable:  "FE",
        Cmd.disable: "FD"
    }

    def __init__(self, host):
        """
        Construtor of the class VW_EGolf:
            :param host: the host of the charger
            :type host:  string
        """
        Device.__init__(self)
        BASE = BASE.format(h=host)
        self.__charging_rate = self.get_charging_rate()

    def command(self, cmd):
        """
        command to the charger:
            :param cmd: the command to pass to the charger
            :type cmd:  Cmd enum
            :return:    if it has been done or not
            :rtype:     bool
        """
        pass
        url    = BASE + __CmdToUrl[cmd]
        result = self._get(url)


    def get_charging_rate(self):
        """charging rate getter from the charger"""
        pass
        url    = BASE + "GC"
        result = self._get(url)
        #sort infos to get the value and return it

    @property
    def charging_rate(self):
        return __charging_rate

    @charging_rate.setter
    def set_charging_rate(self, charging_rate):
        """
        change the charging rate in ampere:
            :param charging_rate: new charging rate
            :type charging_rate: int
            :return:    if it has been done or not
            :rtype:     bool
        """
        pass
        url    = BASE + "SC+" + str(amp)
        result = self._get(url)
        #if $OK then change the attribute
        #self.__charging_rate = charging_rate

class MeterClass(HTTP):
    """
    The MeterClass permit to retrieve datas from the differents data sources on the web using HTTP requests and find the interesting values
    It setups:
        * url:   the destination of the future requests
        * paths: a dictionnary containing the paths to the values used
    """
    def __init__(self, **datas):
        self.data = datas

    def retrieve(self):
        """
        gather informations from the url gave in the config file
        and keep only want we want from the json returned by the GET
        """

        result = dict()

        for k, v in self.data.items():
            val = self._get(v["url"])

            if val is None:
                logging.error("error occured in MeterClass.retrieve: get request failed")
                return val

            json_tree = objectpath.Tree(val)
            result[k] = json_tree.execute(v["path"])

        return result

class Material:

    """
    The main class which contains data of the script
    """

    def __init__(self, path):
        """
        Constructot of the Material Class:
            :param path: the path of the json to parse
            :type path: string
        """
        try:
            with open(path, "r") as f:
                s = f.read()
                s = s.replace('\t','')
                s = s.replace('\n','')
                s = s.replace(',}','}')
                s = s.replace(',]',']')
                data = json.loads(s)
        except Exception as e:
            logging.error("Error occured in Material.__init__: {}".format(e))
            pass

        self.selling_price  = data["selling price"]
        self.start_peak     = data["start peak hour"]
        self.peak_price     = data["peak price"]
        self.start_offpeak  = data["start offpeak hour"]
        self.offpeak_price  = data["offpeak price"]
        self.changing_day_h = data["changing day hour"]

        self.panels    = MeterClass(production=data["meters"]["panels"]["production"], consumption=data["meters"]["panels"]["consumption"])
        self.weather   = MeterClass(temp=data["meters"]["weather"]["temp"])
        self.interval  = data["interval"]
        self.devices   = dict()
        self.day_count = self.time_until_next_midday()

        weather = self.weather_retrieve()
        #the pool pump should be lit for the half of the temperature outside as hours, which give this formula
        ttl = int(weather["temp"] - 273) // 2 * 3600

        #here is the manual part to modify to change the behaviour of this script
        if data["devices"]["pool_pump"]["wired"]:
            self.devices["pool_pump"] = PoolPump(data["devices"]["pool_pump"], ttl)

        if data["devices"]["VW_E-Golf"]["wired"]:
            self.devices["VW_E-Golf"] = VW_EGolf(data["devices"]["VW_E-Golf"]["host"])

    def energy_retrieve(self):
        """encapsulation of the panel data"""
        res = self.panels.retrieve()
        logging.info("energy retrieve done this result: {}".format(res))
        return res

    def weather_retrieve(self):
        """encapsulation of the weather data"""
        res = self.weather.retrieve()
        logging.info("weather retrieve done this result: {}".format(res))
        return res #this temp data is in kelvin

    def count(self):
        """add the interval between the calls to all counts on values"""
        logging.info("adding times on all devices")
        self.day_count -= self.interval
        for dev in self.devices.values():
            dev.count(self.interval)

    def change_day(self):
        """doing the resets needed when changing day"""
        logging.info("changing day of devices")
        self.day_count = 24 * 3600
        for dev in devices.values():
            dev.change_day()

    def time_until_next_midday(self):
        dt = datetime.datetime.now()

        if dt.hour >= 12:
            return ((24 - dt.hour - 1) * 3600) + ((60 - dt.minute - 1) * 60) + (60 - dt.second) + 12 * 3600
        else:
            return ((24 - dt.hour - 1) * 3600) + ((60 - dt.minute - 1) * 60) + (60 - dt.second) - 12 * 3600



class Daemon(step.StepDaemon):
#class Daemon: #Debug

    def pause(self):

        self.pause = True

        try:
            for dev in self.mat.devices.values():
                if isinstance(dev, Gpio):
                    dev.gpio.off()

        except Exception as e:
            logging.info(e)
            print(e)

        str = "Paused process"
        print(str)
        logging.info(str)

    def play(self):

        self.pause = False

        self.do_the_thing()

        str = "Restarted process"
        print(str)
        logging.info(str)

    def stop(self):

        try:
            if hasattr(self, 'mat'):
                for dev in self.mat.devices.values():
                    if isinstance(dev, Gpio):
                        dev.gpio.off()

        except Exception as e:
            logging.info(e)
            print(e)

        finally:
            return super().stop()

    def IsWorthy(self, device):
        """
        determine if this thing is worthy to light
            :param material: the whole object material
            :param device:   the device concerned
            :return:         says if in term of price this is worthy to litten
            :rtype:          bool
        """

        data = self.mat.energy_retrieve()
        now  = time.localtime()

        if data is None:
            logging.error("Daemon.do_the_thing: something went wrong while retrieving data from panels, stopping the lap")
            pass

        if now.tm_hour >= self.mat.start_offpeak or now.tm_hour < self.mat.start_peak: #the price is offpeak
            actual_price = self.mat.offpeak_price
            other_price  = self.mat.peak_price
        else:                                                                # the price is peak
            actual_price = self.mat.peak_price
            other_price  = self.mat.offpeak_price

        return (data["consumption"] + device.Watts - data["production"])*actual_price <= device.Watts*other_price


    def do_the_thing(self):
        """
        setup of booleans to turn off/on the devices availables
        """

        if self.pause:
            pass

        for device in self.mat.devices.values():

            worth_to_light = self.IsWorthy(device)

            if isinstance(device, Gpio):

                if not device.IsEnoughLitten():

                    if not device.gpio.is_lit and worth_to_light:
                        logging.info("turned on {} because it was free to light".format(device))
                        device.gpio.on()

                    elif device.gpio.is_lit and not worth_to_light:
                        logging.info("turned off {} because it no more free to light".format(device))
                        device.gpio.off()

                    elif not device.gpio.is_lit and device.time_to_lit >= self.mat.day_count:
                        logging.info("turned on {} because he has a time-to-lit-a-day".format(device))
                        device.gpio.on()

                else:

                    if device.gpio.is_lit:
                        device.gpio.off()
                        logging.info("turned off {} because it was enough litten".format(device))


    def findcwd(self):
        """
        get the cwd from the pidfile path given by the Daemon
        """
        i = len(self.pidfile) - 1

        while self.pidfile[i] != '/':
            i -= 1

        return self.pidfile[0:(i+1)]

    def step(self):

        """main function"""

        if not hasattr(self, 'initialized'):

            self.initialized = True

            cwd   = self.findcwd()

            self.mat   = Material(os.path.join(cwd, "config.json"))
            self.pause = False

            logging.info("daemon initialized")

        else:

            logging.info("Daemon.run: Starting a lap at: {}".format(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
            self.do_the_thing()
            time.sleep(mat.interval)
            mat.count()
            if mat.day_count < mat.interval:
                mat.change_day()

if __name__ == "__main__": #Debug
    d = Daemon()
    d.run()
