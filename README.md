# Envoy-s Local API
Read data from Photo Voltaïque Enphase Envoy-s Gateway ( see https://enphase.com/fr-fr/produits/envoy/gamme-de-produits )

# Start/stop pool pump when I have too many energy, instead to send to EDF

curl 'http://envoy.local/production.json' | jq                                                                                                                             
{
  "production": [
    {
      "type": "inverters",
      "activeCount": 12,
      "readingTime": 1554648753,
      "wNow": 256,
      "whLifetime": 51771
    },
    {
      "type": "eim",
      "activeCount": 1,
      "measurementType": "production",
      "readingTime": 1554649003,
      "wNow": 215.855,
      "whLifetime": 51705.359,
      "varhLeadLifetime": 0.001,
      "varhLagLifetime": 20128.43,
      "vahLifetime": 66432.568,
      "rmsCurrent": 1.766,
      "rmsVoltage": 223.707,
      "reactPwr": 168.653,
      "apprntPwr": 391.614,
      "pwrFactor": 0.6,
      "whToday": 7416.359,
      "whLastSevenDays": 51705.359,
      "vahToday": 9136.568,
      "varhLeadToday": 0.001,
      "varhLagToday": 2549.43
    }
  ],
  "consumption": [
    {
      "type": "eim",
      "activeCount": 1,
      "measurementType": "total-consumption",
      "readingTime": 1554649003,
      "wNow": 3698.177,
      "whLifetime": 227876.544,
      "varhLeadLifetime": 14297.791,
      "varhLagLifetime": 63965.244,
      "vahLifetime": 262452.791,
      "rmsCurrent": 18.362,
      "rmsVoltage": 223.774,
      "reactPwr": 936.612,
      "apprntPwr": 4108.971,
      "pwrFactor": 0.9,
      "whToday": 39540.544,
      "whLastSevenDays": 228190.544,
      "vahToday": 39240.791,
      "varhLeadToday": 659.791,
      "varhLagToday": 10736.244
    },
    {
      "type": "eim",
      "activeCount": 1,
      "measurementType": "net-consumption",
      "readingTime": 1554649003,
      "wNow": 3482.322,
      "whLifetime": 210082.644,
      "varhLeadLifetime": 14297.79,
      "varhLagLifetime": 43836.814,
      "vahLifetime": 262452.791,
      "rmsCurrent": 16.596,
      "rmsVoltage": 223.84,
      "reactPwr": 1105.265,
      "apprntPwr": 3712.038,
      "pwrFactor": 0.93,
      "whToday": 0,
      "whLastSevenDays": 0,
      "vahToday": 0,
      "varhLeadToday": 0,
      "varhLagToday": 0
    }
  ],
  "storage": [
    {
      "type": "acb",
      "activeCount": 0,
      "readingTime": 0,
      "wNow": 0,
      "whNow": 0,
      "state": "idle"
    }
  ]
}


Data Source URL

https://thecomputerperson.wordpress.com/2016/08/03/enphase-envoy-s-data-scraping/
