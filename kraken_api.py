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

    def check_asset_exists(self, asset_ticker):
        """INPUT : asset pair Ticker
        OUTPUT : 1 if it exists, 0 otherwise"""
        uri = "https://api.kraken.com/0/public/AssetPairs"
        params = {"pair" : asset_ticker}
        response = requests.get(uri, params=params)
        data = json.loads(response.content)

        return 0 if data['error'] else 1

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

    def get_asset_info(self, asset_ticker):
        """INPUT : One or more asset ticker (ex : XETHZUSD[,XBTCZEUR,...])
        OUTPUT : list of asset object infos.
        <pair_name> = pair name
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

        if data['error']:
            print(data['error'])
            return None

        return [data['result'][asset] for asset in data["result"]]

    def get_asset_value(self, asset_ticker, interval=1, since=""):
        """INPUT :
        asset_ticker : asset pair to get OHLC data for (can be a comma separated list)
        interval : time frame interval in minutes (optional):
        1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600
        since = return committed OHLC data since given timestamp (optional.  exclusive)
        OUTPUT : list of asset values
        <pair_name> = pair name
            array of array entries(<time>, <open>, <high>, <low>, <close>, <vwap>, <volume>, <count>)
        last = id to be used as since when polling for new, committed OHLC data"""

        allowed_interval = [1, 5, 15, 30, 60, 240, 1440, 10080, 21160]
        if interval not in allowed_interval:
            print("Wrong interval value")
            return None

        uri = "https://api.kraken.com/0/public/OHLC"
        params = {"pair" : asset_ticker, "interval" : interval, "since" : since}
        response = requests(uri, params)
        data = json.loads(response.content)
        if data['error']:
            print(data['error'])
            return None

        return [data['result'][asset] for asset in data['result']]


if __name__ == '__main__':
    api = KrakenApi()
    thing = api.get_server_time()
    print(thing)

    asset_ticker = "XETHZUSD,XBTCZUSD"

    while 1:
        print(api.check_asset_exists("XETHZUSD"))
        values = api.get_asset_info(asset_ticker)
        print(values)
