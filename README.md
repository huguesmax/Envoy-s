# Envoy-s Local API
Read data from PV (PhotoVoltaïque Enphase Envoy-s Gateway)  ( https://enphase.com/fr-fr/produits/envoy/gamme-de-produits ) and decide if I start/stop my pool pump and start/stop Charging my VW e-Golf


to get solar production status, you can launch this command: 

curl 'http://envoy.local/production.json' | jq 

More informations: 

https://thecomputerperson.wordpress.com/2016/08/03/enphase-envoy-s-data-scraping/

# Config And parameters for Pool Pump

## There are some parameters you manage you pool pump

- 1 Water temperature to determin how long time your pump work

less than 10°C: 2 hours<br/>
Btw 10 & 12°C: 	4 hours<br/>
Btw 12 & 16°C:	6 hours</br>
Btw 16 & 24°C:  8 hours<br/>
Btw 24 & 27°C:  12 hours<br/>
Btw 27 & 30°C:  20 hours<br/>
More than 30°C	24 hours</br>

- 2 Solar Production:

My current installation is PV Production with sell to ENEDIS my Over production. I would like to consum all my kw production instead to sell my kw to ENEDIS and buy later to ENEDIS when I need.

My Current pool pump is 2CV pump ( 1.4kw )  and I have 12 PV Pannels of 300 Watts/Pannel. Due the current lost, my max production is near of 3000W.

### Enphase Envoy-s Gateway return 2 values: 
- Total production in Watt
- Total house comsuption in Watt

we can determin Total Injection to ENEDIS.




