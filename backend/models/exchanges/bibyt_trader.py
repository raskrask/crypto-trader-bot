import requests
import time
import hmac
import hashlib
import json
from config.settings import settings

class BibitTrader:

    def __init__(self):
        pass

    def wallet_balance(self):
        return self._get( "/v5/account/wallet-balance", {
            "accountType": "UNIFIED"  # UNIFIEDまたはCONTRACT（アカウントの種類による）
        })

    def _get(self, endPoint, payload):
        return self._request("GET", endPoint, payload)

    def _post(self, endPoint, payload):
        return self._request("POST", endPoint, payload)

    def _request(self, method, endPoint, payload):
        url = f"{settings.BYBIT_BASE_URL}{endPoint}"
        time_stamp = str(int(time.time() * 10 ** 3))
        recv_window = str(5000)

        httpClient = requests.Session()
        headers = {
            'X-BAPI-API-KEY': settings.BYBIT_API_KEY,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }

        if(method=="POST"):
            param_str= str(time_stamp) + settings.BYBIT_API_KEY + recv_window + json.dumps(payload)
            headers['X-BAPI-SIGN'] = hmac.new(bytes(settings.BYBIT_API_SECRET, "utf-8"), param_str.encode("utf-8"),hashlib.sha256).hexdigest()
            response = httpClient.request(method, url, headers=headers, data=payload)

        else:
            query_string = '&'.join([f"{key}={value}" for key, value in payload.items()])
            param_str= str(time_stamp) + settings.BYBIT_API_KEY + recv_window + query_string
            url = url+"?"+query_string
            headers['X-BAPI-SIGN'] = hmac.new(bytes(settings.BYBIT_API_SECRET, "utf-8"), param_str.encode("utf-8"),hashlib.sha256).hexdigest()
            response = httpClient.request(method, url, headers=headers)

        return response.text
