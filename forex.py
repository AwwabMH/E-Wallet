import requests
import account
import freecurrencyapi
import os

api_key_forex = os.environ.get('api_key_forex')
api_key_Crypto = os.environ.get('api_key_Crypto')

client = freecurrencyapi.Client(api_key_forex)

def get_rate(currency:str):
    
    currency = currency.upper()
    
    if currency in account.forex_supported:

        response_forex = client.latest(currency, currencies=[currencytemp for currencytemp in account.forex_supported if currencytemp != currency])

        response_Crypto = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies={currency}&api_key={api_key_Crypto}")

        if client.status() and response_Crypto.status_code == 200:
        
            response_dict = {"ETH":1/response_Crypto.json()['ethereum'][currency.lower()],
                             "BTC":1/response_Crypto.json()['bitcoin'][currency.lower()],
                             currency:1
                             }
            
            response_dict = response_dict | response_forex['data']

            return response_dict
        
        else:
            return "API Fail"
    
    elif currency in account.currencies_supported:
        
        response_Crypto = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,usd&vs_currencies={currency}&api_key={api_key_Crypto}")
        
        response_forex = client.latest("USD", currencies=[currencytemp for currencytemp in account.forex_supported if currencytemp != "USD"])
        
        if client.status() and response_Crypto.status_code == 200:

            USD_rate = response_Crypto.json()['usd'][currency.lower()]

            response_dict = {"ETH":1/response_Crypto.json()['ethereum'][currency.lower()],
                             "BTC":1/response_Crypto.json()['bitcoin'][currency.lower()],
                             "USD":1/USD_rate,
                             "HKD":((1/USD_rate)*response_forex['data']['HKD']),
                             "EUR":((1/USD_rate)*response_forex['data']['EUR'])
                             }

            return response_dict

        else:
            return "API Fail"

        

        
        
    else:
        return (False, 200)
