# The "Sigmatbot" or simply "Sigmabot" is a project aimed to trade based on a real time data
#The purpose of this release is to demonstrate capabilities of probabilistic approach in
#price action analysis and entry point selection.
#Such algorythm can be used for price to red flag trading for long or short positions during
#price hikes.

#This program runs a sequence of algorythms.

#Prerequisite:
#You need to give it a filename where you have stored the master data.
#Check downloader.py to create such file. 1)put filename for a new .csv file
#2) start it and give 14-20 hours to absorb enough information
#this file row 48 / downloader.py row 22


from analytics_okxx import *
import json
import pickle
import os
import numpy as np
import pandas as pd
from datetime import datetime
from decimal import Decimal
from datetime import timedelta

import okx.Account_api as Account
import okx.Funding_api as Funding
import okx.Market_api as Market
import okx.Public_api as Public
import okx.Trade_api as Trade
import okx.status_api as Status
import okx.subAccount_api as SubAccount
import okx.TradingData_api as TradingData
import okx.Broker_api as Broker
import okx.Convert_api as Convert


import threading
import time
import asyncio
from datetime import datetime
import csv
import json
import hashlib
import base64
import hmac
import requests

#specify the path to the file where historical data is saved
#you make this file using anothe program which purpose is to prepare data for analytics
#we use that program and the data it collected to populate recollections class
path  =  '~/YOUR FOLDER <CHANGE TO YOUR FOLDER /'
filename = 'sigmabot.csv' # HERE YOU PLACE YOUR FILENAME.csv   for example sigmatbot.csv



def read_data(path, filename):
    try:
        df = pd.read_csv(path+filename)[['ts','BTC_price','price_LTC']]
    except:
        pass
    return df 
#READ HISTORY OF PRICE
#df=read_data(path, filename)
df = pd.read_csv(path+filename)[['ts','BTC_price','price_LTC']]
#TAKE LAST 10k records

if len(df) > 50000:
     df = df.tail(50000)

df=df.drop_duplicates()
df = df.tail(10000)
df.reset_index(drop = True, inplace = True)

def run_(path, df, price_reducer, SL_step, price_gap):
    
    file = path + 'trading_data.pkl' #class instance with data container will be saved there
    #need it to control orders

    SL_step_perm = SL_step
    price_gap_perm = price_gap
    #
    lvl=100500
    index_ = -1
    ord_init = 0
    ord_tm=0
    array_=[]
    order_price = []
    order_index = []
    sell_index = []
    close_order_= 0
    sigma=np.zeros((1000,2), dtype=bool)
    
    order_buy = []
    ts_array = []      #to class
    ts = 0             #to class
    cur_ = 'BTC_price'  #to class
    cur2_ = 'price_LTC' #to class
    array_price = []   #to class
    make_order = ""
    time_temp=0
    df = df.drop_duplicates()
    df.reset_index(drop = True, inplace = True)
    df2 = df[0:10000]#populate df=df[0:10000]
    #ts=[]$$$$$$
    array_ = []
    liquidation_price = 0
    #liquidation arrays
    #lvl = 0#????
    make_order = "False"
    search = True#definition of state in this simulation
    thread_cls = order()
    rec_o = recollection(df2, array_price,cur_, cur2_, ts_array, ts)
    get_tickersLTC= 'https://okex.com/api/v5/market/tickers?instType=SWAP'+ '&uly=' + 'LTC-USDT'
    get_tickersBTC= 'https://okx.com/api/v5/market/tickers?instType=SWAP'+ '&uly=' + 'BTC-USDT'
    pricebtc = 40000
    price2ltc = 100
    time_ = 0
    up=0
    down=0
    difference=0

    StartPoint=df['ts'].iloc[-1]+3609676#after we reach this point in time we start trading


    counter=0
    while 1:
        time.sleep(0.1)
        try: 
           requestLTC= requests.get(get_tickersLTC)   

           requestBTC=requests.get(get_tickersBTC)
           try:     
              json_responseLTC = requestLTC.json()
        
              json_responseBTC = requestBTC.json()
 
              time_ = float(json_responseLTC['data'][0]['ts'])
              pricebtc = float(json_responseBTC['data'][0]['last'])
              price2ltc = float(json_responseLTC['data'][0]['last'])
           except:
              pass    
        except:
           pass    
        rec_o.grow(rec_o, pricebtc, price2ltc, time_)
        counter+=1
       # print(counter, rec_o.df_['BTC_price'].iloc[-1])
        if time_ > time_temp:
            time_temp=time_
            sigma[-1][0]=price_drop(10000, rec_o.df_, 'BTC_price', 40, timedelta(hours = 3), timedelta(minutes = 1))
            sigma[-1][1]=price_spike(10000, rec_o.df_, 'BTC_price', 100, timedelta(hours = 3), timedelta(minutes = 1))
            frequency=np.count_nonzero(sigma,axis=0)
            down=frequency[0]
            up=frequency[1]
            sigma  = np.roll(sigma,shift=-1,axis=0)
            lvl=price2ltc
            print('counter',counter,'frequency up',up,' down ',down)
        min_ = rec_o.df_['price_LTC'].min()
        max_ = rec_o.df_['price_LTC'].max()
        difference = float(max_ - min_)/3
        print(difference)

           #35 199
        if up>30 and down>199 and price2ltc < rec_o.df_['price_LTC'].mean() and time_ > StartPoint:

           lvl = price2ltc
           ord_init = lvl #record initial order variables
           liquidation_price = lvl * 0.9

           print('counter',counter,'made order at lvl ', price2ltc) ####################### EVERY CONDITION PLACED HERE<<<<<<<<<<<<<<<<<<<<<<<<<<<<
           print('counter',counter,'frequency up',up,' down ',down,' price',price2ltc)        
                   #PLACE ORD and SL
           try:
               print('test order ')
               result = tradeAPI.place_order(instId='LTC-USD-220930', tdMode='cross' , side='buy', ordType='limit', sz='1', px=str(lvl))
           except:
              pass 

           try:
              result = tradeAPI.place_algo_order(instId='LTC-USD-220930', side='sell', ordType='conditional', sz='1',tdMode='cross', slTriggerPxType='last', slTriggerPx=str(liquidation_price), slOrdPx=str(liquidation_price))
           except:
              pass 

           ord_tm = time_
           make_order = "Done"  #if previous order was liquidated then here we  rewrite prev ord price
           index_ += 1 #index goes into function which starts the thread
        #INCREASE SL and close order
         
        

        while(make_order == "Done" and i < len(df)-1): #place order run a new thread in prod code
              
           counter+=1

           requestLTC= requests.get(get_tickersLTC)


           requestBTC=requests.get(get_tickersBTC)

           json_responseLTC = requestLTC.json()

           json_responseBTC = requestBTC.json()

           time_ = json_response['data'][0]['ts']
           pricebtc = json_responseBTC['data'][0]['last']
           price2ltc = json_responseLTC['data'][0]['last']


           if time > time_temp:
                rec_o.grow(rec_o, pricebtc, price2ltc, time_)
                time_temp=time_
                sigma[-1][0]=price_drop(10000, rec_o.df_, 'BTC_price', 40, timedelta(hours = 3), timedelta(minutes = 1))
                sigma[-1][1]=price_spike(10000, rec_o.df_, 'BTC_price', 100, timedelta(hours = 3), timedelta(minutes = 1))
                frequency=np.count_nonzero(sigma,axis=0)
                down=frequency[0]
                up=frequency[1]
                    #this would be a parallel thread running eternally
                sigma  = np.roll(sigma,shift=-1,axis=0)
           
           if price2ltc > lvl + price_gap:
                 
                 lvl = lvl + SL_step
                 
                 #INCREASE SL>
                 try: 
                    print('test SL increase')
                    result = tradeAPI.place_algo_order(instId='LTC-USD-220930', side='sell', ordType='conditional', sz='1',tdMode='cross', slTriggerPxType='last', slTriggerPx=str(lvl),slOrdPx=str(lvl))
                 except:
                    pass 
                 print('lvl: ',lvl,' SL increment: ',SL_step)
                 lvl = lvl + SL_step
                 price_gap=1.9
                 SL_step=1
                 increment_ = "price increased"
                 print(' n lvl:', lvl)
                 #INCREASE SL^
           if price2ltc < lvl and increment_ == "price increased": #change
                 #######CHECK ORDER CLOSED OR OPENED
                 close_order_ = lvl
                 search = True
                 make_order = "False"
                 liquidation_price = 0
                 print('order closed in profit')
                 print('lvl: ', lvl, "index_", index_)
                 lvl = 100500
                 thread_cls.order_open_price[index_] = ord_init
                 thread_cls.open_time[index_] = ord_tm
                 thread_cls.order_close_price[index_] = close_order_
                 thread_cls.close_time[index_] = time_
                 thread_cls.order_sl[index_] = liquidation_price
                 thread_cls.wage[index_] = (ord_init - close_order_ - liquidation_price) * (-1)
                 SL_step = SL_step_perm
                 price_gap = price_gap_perm
                 with open(name, 'wb') as file:
                    pickle.dump(thread_cls, file)
           if liquidation_price > price2ltc:
                 close_order_ = 0
                 search = True
                 make_order = "False"
                 pprice2ltcrint('order closed at liquidation_price ', liquidation_price)
                 lvl = 100500
                 fill(ord_init,ord_tm,close_order_,time,liquidation_price)
                 thread_cls.order_open_price[index_] = ord_init
                 thread_cls.open_time[index_] = ord_tm
                 thread_cls.order_close_price[index_] = close_order_
                 thread_cls.close_time[index_] = time_
                 thread_cls.order_sl[index_] = liquidation_price
                 thread_cls.wage[index_] = (ord_init - close_order_ - liquidation_price) * (-1)
                 SL_step = SL_step_perm
                 price_gap = price_gap_perm
                 with open(name, 'wb') as file:
                    pickle.dump(thread_cls, file)
        increment_="none"




api_key = "Your Api Key"
secret_key = "Get it when make api key"
passphrase = "You specify it yourself when create an api key"
    # flag flag is the key parameter which can help you to change between demo and real trading.
    # flag = '1'  #  demo trading
flag = '0'  #  real trading

    # account api
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)

    # funding api
fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)

    # convert api
convertAPI = Convert.ConvertAPI(api_key, secret_key, passphrase, False, flag)

    # market api
marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, True, flag)

    # public api
publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)

    # trading data
tradingDataAPI = TradingData.TradingDataAPI(api_key, secret_key, passphrase, False, flag)

    # trade api
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
    #   Place Order



#Specialied vars   are  ord_init and volume, liquidation_price, lvl for SL orders.
###########################  Limit Order   ###########################   

#    result = tradeAPI.place_order(instId='LTC-USD-220930', tdMode='cross' , side='buy', ordType='limit', sz='volume', px='ord_init')


###########################   SL Order   ###########################

#    result = tradeAPI.place_algo_order(instId='LTC-USD-220930', side='sell', ordType='conditional', sz='1',tdMode='cross', slTriggerPxType='last', slTriggerPx='89',slOrdPx='89')


########################################################################




    # API subAccount
subAccountAPI = SubAccount.SubAccountAPI(api_key, secret_key, passphrase, False, flag)

    # BrokerAPI
BrokerAPI = Broker.BrokerAPI(api_key, secret_key, passphrase, False, flag)

    #system status
Status = Status.StatusAPI(api_key, secret_key, passphrase, False, flag)
    # result = Status.status()

tr = threading.Thread(target = run_(path, df, 0.1, 2, 3.5))

if __name__ == '__main__':
    tr.start()
