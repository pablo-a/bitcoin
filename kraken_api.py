# coding=utf-8
import requests
import json
from datetime import datetime
import time

# All API URLs should use the domain api.kraken.com.

# Public methods can use either GET or POST.

# Private methods must use POST and be set up as follows:
# HTTP header:
# API-Key = API key
# API-Sign = Message signature using HMAC-SHA512 of (URI path + SHA256(nonce + POST data)) and base64 decoded secret API key
# POST data:
# nonce = always increasing unsigned 64 bit integer
# otp = two-factor password (if two-factor enabled, otherwise not required)





class KrakenApi(object):
    """docstring de la classe KrakenApi : """

    def get_server_time(self):
        """response time is approximative and supposed to be UTC. (-1h. careful with changement d'heure!)
        exemple response :
        {  "error": [],
           "result": {
              "unixtime": 1497624192,
              "rfc1123": "Fri, 16 Jun 17 14:43:12 +0000"}
        }"""

        uri = "https://api.kraken.com/0/public/Time"
        response = requests.get(uri)
        data = json.loads(response.content)

        date_object = datetime.fromtimestamp(data["result"]['unixtime'])
        print date_object

        return (data['result']["unixtime"], date_object)

    def get_asset_value(self, asset_ticker):
        """INPUT : One or more asset ticker (ex : XETHZUSD[,XBTCZUSD,...])
        OUTPUT : list of asset object infos.
        a = ask array(<price>, <whole lot volume>, <lot volume>),
        b = bid array(<price>, <whole lot volume>, <lot volume>),
        c = last trade closed array(<price>, <lot volume>),
        v = volume array(<today>, <last 24 hours>),
        p = volume weighted average price array(<today>, <last 24 hours>),
        t = number of trades array(<today>, <last 24 hours>),
        l = low array(<today>, <last 24 hours>),
        h = high array(<today>, <last 24 hours>),
        o = today's opening price"""

        uri = "https://api.kraken.com/0/public/Ticker"
        params = {"pair" : asset_ticker}

        response = requests.get(uri, params=params)
        data = json.loads(response.content)
        return [asset for asset in data["result"]]


if __name__ == '__main__':
    api = KrakenApi()
    thing = api.get_server_time()
    print(thing)

    asset_ticker = "XETHZUSD"
    values = api.get_asset_value(asset_ticker=)
    print(values)




    
