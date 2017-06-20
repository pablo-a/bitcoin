# coding=utf-8
import requests
from urllib import urlencode
import json
from datetime import datetime
import time
# private query signing
import hashlib
import hmac
import base64


# All API URLs should use the domain api.kraken.com.

# Public methods can use either GET or POST.

# Private methods must use POST and be set up as follows:
# HTTP header:
# API-Key = API key
# API-Sign = Message signature using HMAC-SHA512 of (URI path + SHA256(nonce + POST data)) and base64 decoded secret API key
# POST data:
# nonce = always increasing unsigned 64 bit integer
# otp = two-factor password (if two-factor enabled, otherwise not required)

# inheritance of object for python2 compatibility
class KrakenApi(object):
    """docstring de la classe KrakenApi : """


    def __init__(self):
        with open("credentials.txt", "r") as f:
            # api_key (str) – key required to make queries to the API
            self.api_key = f.readline().strip()
            # secret (str) – private key used to sign API messages
            self.secret = f.readline().strip()

    def _private_query(self, uri, postdata={}):
        """Generic method to perform private requests using Kraken API.
        INPUT :
        uri : the prefix where to find ressource ('/0/private/TradeBalance')
        postdata : dictionnary with request data.

        OUTPUT :
        request result (dictionnary or None if an error occured)"""


        base_url = "https://api.kraken.com"

        postdata['nonce'] = int(3*time.time())
        postdata_encoded = urlencode(postdata)

        # Nonce + postdata
        encoded = (str(postdata['nonce']) + postdata_encoded)
        # URI + SHA256(Nonce + postdata)
        message = uri + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        headers = {
            'API-Key': self.api_key,
            # Message signature using HMAC-SHA512 of
            # (URI path + SHA256(nonce + POST data)) and base64 decoded secret API key
            'API-Sign': sigdigest
        }

        url = base_url + uri
        response = requests.post(url, data=postdata, headers=headers)
        return json.loads(response.content)

    def check_asset_exists(self, asset_ticker):
        """INPUT : asset pair Ticker (eg. XETHZUSD)
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

    def get_trading_asset_details(self, asset_ticker):
        """Useful for more details like leverage, fees, margin on an asset.

        INPUT :
        info = info to retrieve (optional):
            info = all info (default)
            leverage = leverage info
            fees = fees schedule
            margin = margin info
        pair = comma delimited list of asset pairs to get info on (optional.  default = all)

        OUTPUT : list of asset_pair detail_info.
        <pair_name> = pair name
            altname = alternate pair name
            aclass_base = asset class of base component
            base = asset id of base component
            aclass_quote = asset class of quote component
            quote = asset id of quote component
            lot = volume lot size
            pair_decimals = scaling decimal places for pair
            lot_decimals = scaling decimal places for volume
            lot_multiplier = amount to multiply lot volume by to get currency volume
            leverage_buy = array of leverage amounts available when buying
            leverage_sell = array of leverage amounts available when selling
            fees = fee schedule array in [volume, percent fee] tuples
            fees_maker = maker fee schedule array in [volume, percent fee] tuples (if on maker/taker)
            fee_volume_currency = volume discount currency
            margin_call = margin call level
            margin_stop = stop-out/liquidation margin level"""

        uri = "https://api.kraken.com/0/public/AssetPairs"
        params = {"pair" : asset_ticker}
        response = requests.get(uri, params=params)
        data = json.loads(response.content)
        if data['error']:
            print(data['error'])
            return None
        return [data['result'][asset] for asset in data['result']]

    def get_asset_info(self, asset_ticker):
        """INPUT : One or more asset ticker (ex : XETHZUSD[,XBTCZEUR,...])

        OUTPUT : list of asset object infos.
        <pair_name> = pair name
            ask = ask array(<price>, <whole lot volume>, <lot volume>),
            bid = bid array(<price>, <whole lot volume>, <lot volume>),
            last_trade = last trade closed array(<price>, <lot volume>),
            volume = volume array(<today>, <last 24 hours>),
            weighted_volume = volume weighted average price array(<today>, <last 24 hours>),
            trade_nb = number of trades array(<today>, <last 24 hours>),
            low = low array(<today>, <last 24 hours>),
            high = high array(<today>, <last 24 hours>),
            open = today's opening price"""

        key_conversion = {
            "a" : "ask",
            "b" : "bid",
            "c" : "last_trade",
            "v" : "volume",
            "p" : "weighted_volume",
            "t" : "trade_nb",
            "l" : "low",
            "h" : "high",
            "o" : "open"
        }

        uri = "https://api.kraken.com/0/public/Ticker"
        params = {"pair" : asset_ticker}
        response = requests.get(uri, params=params)
        data = json.loads(response.content)

        if data['error']:
            print(data['error'])
            return None

        # change keys name then return result
        for asset in data['result']:
            for old_key in key_conversion:
                new_key = key_conversion[old_key]
                data['result'][asset][new_key] = data['result'][asset].pop(old_key)
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

    def get_order_book(self, asset_ticker, count="all"):
        """fetch the market depth for an asset.
        INTPUT :
        pair = asset pair to get market depth for
        count = maximum number of asks/bids (optional)

        OUTPUT : array of pair name and recent trade data
        <pair_name> = pair name
            asks = ask side array of array entries(<price>, <volume>, <timestamp>)
            bids = bid side array of array entries(<price>, <volume>, <timestamp>)"""

        uri = "https://api.kraken.com/0/public/Depth"
        params = {"pair" : asset_ticker, "count" : count}
        response = requests.get(uri, params=params)
        data = json.loads(response.content)
        if data['error']:
            print(data['error'])
            return None

        return data['result'][asset_ticker]

    def get_recent_trade(self, asset_ticker, since=""):
        """INPUT :
        pair = asset pair to get trade data for (only one)
        since = return trade data since given id (optional.  exclusive)

        OUTPUT : array of pair name and recent trade data
        <pair_name> = pair name
            array of array entries(<price>, <volume>, <time>, <buy/sell>, <market/limit>, <miscellaneous>)
        last = id to be used as since when polling for new trade data"""

        uri = "https://api.kraken.com/0/public/Trades"
        params = {"pair" : asset_ticker, "since" : since}
        response = requests.get(uri, params=params)
        data = json.loads(response.content)
        if data['error']:
            print(data['error'])
            return None

        return data['result'][asset_ticker]

    def get_recent_spread(self, asset_ticker, since=""):
        """INPUT :
        pair = asset pair to get spread data for
        since = return spread data since given id (optional.  inclusive)

        OUTPUT : array of pair name and recent spread data
        <pair_name> = pair name
            array of array entries(<time>, <bid>, <ask>)
        last = id to be used as since when polling for new spread data"""

        uri = "https://api.kraken.com/0/public/Spread"
        params = {"pair" : asset_ticker, "since" : since}
        response = requests.get(uri, params=params)
        data = json.loads(response.content)
        if data['error']:
            print(data['error'])
            return None

        return data['result'][asset_ticker]

    # start of private methods (account needed)
    def get_account_balance(self):
        """Result: array of asset names and balance amount"""
        uri = "/0/private/Balance"
        data = self._private_query(uri)
        return data

    def get_trade_balance(self):
        uri = "/0/private/TradeBalance"
        data = self._private_query(uri, postdata={"asset" : ""})
        return data

    def get_open_orders(self):
        uri = "/0/private/OpenOrders"
        data = self._private_query(uri)
        return data

if __name__ == '__main__':
    api = KrakenApi()

    wrong_ticker = "XETHZUSD,XBTCZUSD"
    asset_ticker = "XETHZUSD,DASHEUR"
    single_ticker = "XETHZUSD"

    # kind of unit_testing
    print(api.get_server_time())

    # PRIVATE :
    print(api.get_account_balance())
    print(api.get_trade_balance())
    print(api.get_open_orders())
    # print(map(api.get_recent_spread, [wrong_ticker, asset_ticker, single_ticker]))


    # print(api.get_recent_trade(wrong_ticker))
    # print(api.get_recent_trade(asset_ticker))
    # print(api.get_recent_trade(single_ticker, since=time.time()))

    # print(api.get_asset_info(asset_ticker))
    # print(api.get_asset_info(wrong_ticker))
    #
    # print(api.check_asset_exists("XETHZUSD"))
    #
    # print(api.get_order_book(single_ticker, count=10))
    #
    # print(api.get_trading_asset_details(asset_ticker))
