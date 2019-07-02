package main

import (
	"reflect"

	"github.com/elgs/gojq"
)

const (
	baseFloat = 0.1
)

var stringToDevice = map[string]DeviceConstructor{
	"pool_pump": NewPoolPump,
	"VW_E-Golf": New_VW_EGolf,
}

var stringToMeter = map[string]MeterConstructor{
	"panels":  NewPanels,
	"weather": NewWeather,
}

//Parser is the model struct
type Parser struct {
	Interval         float64 `json:"interval"`
	ChangingDayHour  float64 `json:"changing day hour"`
	StartPeakHour    float64 `json:"start peak hour"`
	StartOffpeakHour float64 `json:"start offpeak hour"`
	PeakPrice        float64 `json:"peak price"`
	OffpeakPrice     float64 `json:"offpeak price"`
	SellingPrice     float64 `json"selling price`
	Devices          map[string]IDevice
	Meters           map[string]IMeter
}

//Parse is the main parsing function
func Parse(confFile string) (*Parser, error) {

	file, err := gojq.NewFileQuery(confFile)
	if err != nil {
		return nil, err
	}

	d := &Parser{}
	elts := reflect.ValueOf(d).Elem()
	tags := reflect.TypeOf(d).Elem()
	base := reflect.ValueOf(baseFloat)

	for i := 0; i < elts.NumField(); i++ {

		field := elts.Field(i)

		if field.Type() == base.Type() {

			tag := tags.Field(i).Tag.Get("json")

			v, err := file.QueryToFloat64(tag)
			if err == nil {
				field.SetFloat(v)
			}
		}
	}

	return d, nil
}
