package main

import (
	"fmt"
	"reflect"

	"github.com/elgs/gojq"
)

const (
	confFile  = "config.json"
	baseFloat = 0.1
)

type Parser struct {
	Interval         float64 `json:"interval"`
	ChangingDayHour  float64 `json:"changing day hour"`
	StartPeakHour    float64 `json:"start peak hour"`
	StartOffpeakHour float64 `json:"start offpeak hour"`
	PeakPrice        float64 `json:"peak price"`
	OffpeakPrice     float64 `json:"offpeak price"`
	SellingPrice     float64 `json"selling price`
}

func main() {

	file, err := gojq.NewFileQuery(confFile)
	if err != nil {
		panic(err)
	}

	d := Parser{}
	elts := reflect.ValueOf(&d).Elem()
	tags := reflect.TypeOf(&d).Elem()
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

	fmt.Println(d.Interval)
	fmt.Println(d.ChangingDayHour)
}
