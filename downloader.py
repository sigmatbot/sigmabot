# The "Sigmatbot" or simply "sigmabot" is a project aimed to trade based on a real time data

#               the general sequence of action is below
# 0)read master data 1)sign 2)make calculation and projection 3)make a trade 4)record

#We need a historical(master) data. This specific program surves the purpose of data collection using REST API.
#Records BTC, LTC, MATIC price and ofcourse timestamp. Some other data for future research.

import threading
import time
import asyncio
from datetime import datetime
hold_before_buy = 8
import csv
import json
import hashlib
import base64
import hmac
import requests

okexurl = "https://okex.com"
filename = 'sigmabot.csv' #<<<<<<<<<<<<<<<<<<<<<<<<<<<
time_ = datetime.now()
timestamp_ = datetime.timestamp(time_)
##########FUNCTION USED TO CONSTRUCT  HEADERS WITH PRESENT TIMESTAMP
def mq(str_,headers):
    querry=str_
    headers=headers
    url="https://okx.com/api/v5/trade/order"
    API_Key = "YOUR KEY" #not required for this program now but might be used in future versions with API requests like mark price etc.
    API_SECRET = "YOUR SECRET KEY"
    PASSPHRASE = "YOUR PASSPHRASE"
    TIMESTAMP = datetime.utcnow().isoformat(timespec='milliseconds')
#res=""
#simple_string=""
#encoded_simple_string=""
#SecretKey_Byte=""
#Base64_msg=""
    simple_string = TIMESTAMP + 'POST' + 'api/v5/trade/order'
    encoded_simple_string = simple_string.encode()
    SecretKey_Byte = bytes(API_SECRET,'UTF-8')
    res=hmac.new(SecretKey_Byte, encoded_simple_string, hashlib.sha256).hexdigest()
    Base64_msg = base64.b64encode(res.encode())

    headers = {}
    headers['Content-type'] = 'application/json'
    headers['OK-ACESS-KEY'] = API_Key
    headers['OK-ACCESS-SIGN'] = Base64_msg
    headers['OK-ACCESS-TIMESTAMP'] = TIMESTAMP
    headers['OK-ACCESS-PASSPHRASE'] = PASSPHRASE

    time_ = datetime.now()
    timestamp_ = datetime.timestamp(time_)
    pair_1 = "XRP"
    pair_2 = "USDT"
    price = str(0.2)
    order_qty = str(0.1)
    body =  make_trade_request(pair_1, pair_2, "cash", "buy", "limit", price, order_qty)

    response=requests.get(okexurl, data=body, headers=headers)
    time.sleep(0.1)
    json_response = response.json()
    print(json_response)
    return json_response
   
def make_trade_request(pair_1,pair_2,Trade_mode, side_buy_or_sell, order_Type, order_value, qty):
    str={}
    str['instId'] = pair_1 + '-' + pair_2
    str['tdMode'] = Trade_mode
    str['side'] = side_buy_or_sell
    str['ordType'] = order_Type
    str['px'] = order_value
    str['sz'] = qty
    return str

pair_1 = "XRP"
pair_2 = "USDT"
price = str(0.2)
order_qty = str(0.1)
body=make_trade_request(pair_1, pair_2, "cash", "buy", "limit", price, order_qty)
print('start')

headers={}
response=requests.get(okexurl, data=body, headers=headers)
instrument = 'ELON-USDT'
get_tickers= 'https://okx.com/api/v5/market/tickers?instType=SWAP'+ '&uly=' +instrument
rr2= requests.get(get_tickers)
time.sleep(1)
json_response = rr2.json()
price=json_response['data'][0]['last']

get_datalink= 'https://okx.com/api/v5/market/instruments?instType=SWAP'+ '&uly='+instrument

#Primary function to download info simultaneously.
def get_current_data():
   count_=1
   count2=0
   with open(filename, mode='a+') as orders_file:
      orders_writer = csv.writer(orders_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      orders_writer.writerow(['N','ts','BTC_price','price_LTC','vol24','ask_l1','ask_l2','vol1_L1','V1L2','bids_l1','bids_l2','vol2_L1', 'V2L2', 'price_MATIC'])
      get_taker_vloume= 'https://okx.com/api/v5/rubik/stat/taker-volume?ccy' + 'LTC' + '&instType=SPOT'
      get_tickers= 'https://okx.com/api/v5/market/tickers?instType=SWAP'+ '&uly=' + 'LTC-USDT'
      gob= 'https://okx.com/api/v5/market/books?instId=' + 'LTC-USDT' + '&sz=2'
      get_tickersBTC= 'https://okx.com/api/v5/market/tickers?instType=SWAP'+ '&uly=' + 'BTC-USDT'
      get_tickersMATIC= 'https://okx.com/api/v5/market/tickers?instType=SWAP'+ '&uly=' + 'MATIC-USDT'
      count2 = 0
      rows_to_record = 500000
      while count2<rows_to_record:

         try:
 
            r=requests.get(gob)
    
            time.sleep(0.1)
         
            rr2= requests.get(get_tickers)
            rrMATIC = requests.get(get_tickersMATIC) 
        
        
            jr = r.json()
        
            
            r_b=requests.get(get_tickersBTC)
        
        
         
            jr_btc=r_b.json()
         
            jrMATIC = rrMATIC.json()
                  
            json_response = rr2.json()
        
            
    
            ts = json_response['data'][0]['ts']
            vol24 = json_response['data'][0]['vol24h']
            price=json_response['data'][0]['last']
            price_btc = jr_btc['data'][0]['last']
            price_MATIC = jrMATIC['data'][0]['last']
            
            
            ask = []
            bid = []
            vol_ask = []
            vol_bid = []
            try:
               for i  in range(0,len(jr['data'][0]['asks'])):
                  ask.append(jr['data'][0]['asks'][i][0])
                  vol_ask.append(jr['data'][0]['asks'][i][1])
                  bid.append(jr['data'][0]['bids'][i][0])
                  vol_bid.append(jr['data'][0]['bids'][i][1])
               orders_writer.writerow([count2, ts,price_btc, price, vol24,ask[0],ask[1],vol_ask[0],vol_ask[1],bid[0],bid[1],vol_bid[0], vol_bid[1], price_MATIC])
            except:
                pass        
        
            check_to_output=count2 % 10
            if check_to_output == 0:
                print('row:', count2, ' of ',rows_to_record)
            count2 += 1
         except:
             print('problem')

t1 = threading.Thread(target=get_current_data)

if __name__ == "__main__":
     t1.start()
