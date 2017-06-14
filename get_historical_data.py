# coding=utf-8
import requests
import json
import pandas as pd

def main():
    lst_plat = ["krakenUSD", "bitfinexUSD", "bitstampUSD", "btceUSD"]
    for plateforme in lst_plat:
        url = ("https://bitcoincharts.com/charts/chart.json?m=%s&SubmitButton"
        "=Draw&r=&i=&c=0&s=&e=&Prev=&Next=&t=S&b=&a1=&m1=10&a2=&m2=25&x=0&i1=&i2=&i3"
        "=&i4=&v=1&cv=0&ps=0&l=0&p=0&")
        url = url % plateforme

        json_response = requests.get(url)
        data = json.loads(json_response.content)
        # for elem in data:
        #     print(elem)

        lst_date = [elem[0] for elem in data]
        lst_open = [elem[1] for elem in data]
        lst_high = [elem[2] for elem in data]
        lst_low = [elem[3] for elem in data]
        lst_close = [elem[4] for elem in data]
        lst_volume_bitcoin = [elem[5] for elem in data]
        lst_volume_currency = [elem[6] for elem in data]
        lst_price = [elem[7] for elem in data]

        ts_to_date_formula = "=(((/60)/60)/24)+DATE(1970;1;1)"

        # df = pd.DataFrame([lst_date, lst_open, lst_high, lst_low, lst_close,
        # lst_volume_bitcoin, lst_volume_currency, lst_price])


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
