# coding=utf-8
import requests
import json
import sys
import pandas as pd

def main():
    """USAGE :
    python get_historical_data.py

    main parameters :
    m = Exchange plateforme
    r = number of days of data since today. (all time if empty.)
    i = intervalle of time between each point."""

    lst_plat = ["krakenUSD", "bitfinexUSD", "bitstampUSD", "btceUSD"]
    lst_intervalle = ["1-min", "5-min", "15-min", "30-min", "Hourly", "2-hour",
    "6-hour", "12-hour", "Daily", "Weekly"]

    for plateforme in lst_plat:
        url = ("https://bitcoincharts.com/charts/chart.json?m=%s&SubmitButton"
        "=Draw&r=&i=%s&c=0&s=&e=&Prev=&Next=&t=S&b=&a1=&m1=10&a2=&m2=25&x=0&i1=&i2=&i3"
        "=&i4=&v=1&cv=0&ps=0&l=0&p=0&")

        interval = "30-min"
        url = url % (plateforme, interval)

        json_response = requests.get(url)
        data = json.loads(json_response.content)

        lst_date = [elem[0] for elem in data]
        lst_open = [elem[1] for elem in data]
        lst_high = [elem[2] for elem in data]
        lst_low = [elem[3] for elem in data]
        lst_close = [elem[4] for elem in data]
        lst_volume_bitcoin = [elem[5] for elem in data]
        lst_volume_currency = [elem[6] for elem in data]
        lst_price = [elem[7] for elem in data]

        df = pd.DataFrame({
            "date" : lst_date,
            "open" : lst_open,
            "high" : lst_high,
            "low" : lst_low,
            "close" : lst_close,
            "volume (BTC)" : lst_volume_bitcoin,
            "volume (USD)" : lst_volume_currency,
            "price" : lst_price
        })

        file_name = plateforme + ".xlsx"
        # ["date", "open", "high", "low", "close", "volume (BTC)", "volume (USD)", "price"]
        df.to_excel(file_name, header=True, index=False)


if __name__ == '__main__':
    main()
