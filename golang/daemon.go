// THIS GO SCRIPT IS JUST A TRANSPOSITION OF THE PYTHON SCRIPT
package main

import (
	"io/ioutil"
	"log"
	"net/http"

	"github.com/elgs/gojq"
	"github.com/takama/daemon"
)

//DeviceConstructor is the delegate for the constructor of device structs
type DeviceConstructor func(int, int) IDevice

//MeterConstructor is the delegate for the constructor of meter structs
type MeterConstructor func(map[string]string) IMeter

func checkErr(err error) {
	if err != nil {
		log.Fatalln(err)
	}
}

// Service has embedded daemon
type Service struct {
	daemon.Daemon
}

//Device is the base device struct
type Device struct {
	Wired     bool `json:"wired"`
	Watts     int  `json:"Wh"`
	timeLit   int
	timeToLit int
}

//IDevice is the base interface for output
type IDevice interface {
	On()
	Off()
	Count(int)
	IsLit() bool
	ChangeDay(int)
	IsEnoughLitten() bool
}

//ChangeDay reset values of timelit and timeToLit
func (d Device) ChangeDay(ttl int) {
	d.timeLit = 0
	d.timeToLit = ttl
}

//IsEnoughLitten return a bool to light or not to light the device
func (d Device) IsEnoughLitten() bool {
	return d.timeLit >= d.timeToLit
}

//Count the time between intervals
func (d Device) Count(i int) {
	d.timeLit += i
}

//PoolPump is the only usable class for now
type PoolPump struct {
	Device
	//GPIO NotImplemented
}

//IsLit says if the gpio is lit
func (d PoolPump) IsLit() bool {
	return true
}

//On turns on the GPIO
func (d PoolPump) On() {

}

//Off Turns off the GPIO
func (d PoolPump) Off() {

}

//NewPoolPump is the pseudo-constuctor for the Device class
func NewPoolPump(watts int, ttl int) IDevice {
	dev := PoolPump{}
	dev.Watts = watts
	dev.ChangeDay(ttl)
	return dev
}

//IMter is The base interface for meter
type IMeter interface {
	retrieve() map[string]float64
}

//Get base http query
type Get struct {
	url string
}

//Compute the get request
func (g *Get) Compute(paths map[string]string) map[string]float64 {
	//Compute the get command
	if g.url == "" {
		log.Fatalln("a http get function need a url")
	}

	resp, err := http.Get(g.url)
	checkErr(err)

	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	checkErr(err)

	result := make(map[string]float64)

	parser, err := gojq.NewStringQuery(string(body))
	checkErr(err)

	for k, v := range paths {
		result[k], err = parser.QueryToFloat64(v)
		checkErr(err)
	}

	return result
}
