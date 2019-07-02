// THIS GO SCRIPT IS JUST A TRANSPOSITION OF THE PYTHON SCRIPT
package maine

import (
	"io/ioutil"
	"log"
	"net/http"

	"github.com/elgs/gojq"
	"github.com/takama/daemon"
)

func checkErr(err error) {
	if err != nil {
		log.Fatalln(err)
	}
}

// Service has embedded daemon
type Service struct {
	daemon.Daemon
}

//Device base struct
type Device struct {
	Wired     bool
	Watts     int
	timeLit   int
	timeToLit int
}

//ChangeDay reset values of timelit and timeToLit
func (d *Device) ChangeDay(ttl int) {
	d.timeLit = 0
	d.timeToLit = ttl
}

//IsEnoughLitten return a bool to light or not to light the device
func (d *Device) IsEnoughLitten() bool {
	return d.timeLit >= d.timeToLit
}

//NewDevice is the pseudo-constuctor for the Device class
func NewDevice(watts int, ttl int) Device {
	dev := Device{Watts: watts}
	dev.ChangeDay(ttl)
	return dev
}

//PoolPump is the only usable device class
type PoolPump struct {
	Device
	//gpio GPIO
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
