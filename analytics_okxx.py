#GNU GENERAL PUBLIC LICENSE
import os
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from datetime import datetime
from decimal import Decimal
from datetime import timedelta
import pickle

#######         BASIC IDEA   1     ######
#RECORD POSITION OF DELTA BASED ON MEDIAN
#CALCULATE PRICE DELTA
#SEARCH FOR  OUTLIERS (RISE OR FALL)
#######RECORD OUTLIER INDEX
#DETECT T OR F INFLUENCE OF ASK AND BID ORDERS
#A B test comparisson

############Calculation principle###########
#----------------/////////////////-------lv3
#                    /
#                   /--------------------------***emit
#                  /
#------------////////--------------------lv2
#                 \
#                  \---------------------------***absorb
#                   \
#-----------------///////////////---------lv1
#price1 to price2 to price3 to price to ... ∞
#every change in price represents a shift in a level
#LOCAL base level-<origin> is selected from the price data
#before the outlier occurrence

#######         BASIC IDEA   2     ######
#dnwd mvmnt
#0 __________
#1 \ short  /  /\                       12
#2  \      /  /  \                      11
#3   \    /  /    \                     10
#4    \  /  / long \                    9
#5     \/\ /________\/\ ______________  8
#6      \//          \/ \ liquidation/  7
#7                       \          /   6
#8                        \        /    5      /\
#9                         \      /     4     /  \
#10                         \    /      3    /    \
#11                          \  /       2/\ / long \
#12                           \/        1\//________\
#                                       0
#take time to make orders to let directions of price to move after liquidaton
#you can likely long immediatly after short position close in *certain conditions*




def change_time(tm):
    return datetime.fromtimestamp(int(str(tm)[:-3])).strftime("%A, %B %d, %Y %I:%M:%S")


batch = 10000
four_hours = 4
MA10 = 10
MA20 = 20
MA50 = 50
tpersecond=1
takeseconds=4
frequency=1/tpersecond
pos_shift = frequency*takeseconds

# HOW IT WORKS
##makes arrays of columns containing location baseed  boolean presence data. One group of arrays for UCL, another for LCL
## if the outlier is present in the given interval the value is true. Intervals are rolling and isolated for each iteration.
def pos_UCL(df,column_name,pos_shift):
   delta = populate_delta_array(df,column_name,pos_shift).dropna()
   UCL= delta.mean() + 3* delta.std()
   return delta.loc[delta > UCL]

def pos_LCL(df,column_name,pos_shift):
   delta = populate_delta_array(df,column_name,pos_shift).dropna()
   LCL= delta.mean() - 3* delta.std()
   return delta.loc[delta < LCL]

#speed of price change
def populate_delta_array(data,name,pos_shift):
   return data[name]-data[name].shift(pos_shift)
   
#four_hours=4


def outlier(dir, df, column_name, pos_shift):
   dir = dir
   if dir ==  'up':
      try:
         positions_ = pos_UCL(df,column_name,pos_shift)
         p=find_locals(positions_)
      except:
         p=[]
         return p
   if dir == 'down':
      try:
         positions_ = pos_LCL(df,column_name,pos_shift)
         p=find_locals(positions_)
      except:
         p=[]
         return p
   return p #record every outlier in df and pass it to find locals


   #return array [start of speed increment position][end of increment occurrence(index)]. Use it to find spikes in price in find_sigma  function.
def find_locals(positions_): #index of outlier sequence occurrence
   start_end = []
   a = []
   a.append(positions_.index[0])
   a.append(positions_.index[0])
   for i in range(1,len(positions_.index)):
       if positions_.index[i]-positions_.index[i-1] < 3:
          a[1] = positions_.index[i]
       else:
          start_end.append(a)
          a = []
          a.append(positions_.index[i])
          a.append(positions_.index[i])
   return start_end


def find_sigma(dir, df, column_name, pos_shift, bound_low, bound_high):
   e=False
   p_o = outlier(dir, df, column_name, pos_shift)
   for tm_pos in range(0,len(p_o)):#check if some outlier is present in given bounds
      if (tm_(df['ts'][p_o[tm_pos][1]]) > tm_(df['ts'][i])-bound_low) and (tm_(df['ts'][p_o[tm_pos][1]]) < tm_(df['ts'][i])-bound_high):
         e=True
   return e

def price_drop(size, df, column_name, pos_shift, bound_low, bound_high):
   drop_=False
   df=df
   dir='down'
  # i position for moment in time for which we calculate array of outliers and do comparisson
   try:
      outliers_=pos_LCL(df,column_name,pos_shift)
   except:
      p = pd.Series()
      return p
   for i in outliers_.index:
      if (tm_(df['ts'][i]) > tm_(df['ts'][9999])-bound_low) and (tm_(df['ts'][i]) < tm_(df['ts'][9999])-bound_high):
             drop_=True
   return drop_

def price_spike(size, df, column_name, pos_shift, bound_low, bound_high):
   spike=False
   df=df
   dir='up'
# i position for moment in time for which we calculate array of outliers and do comparisson
   try:
      outliers_=pos_UCL(df,column_name,pos_shift)
   except:
      p = n = pd.Series()
      return p
   for i in outliers_.index:
      if (tm_(df['ts'][i]) > tm_(df['ts'][9999])-bound_low) and (tm_(df['ts'][i]) < tm_(df['ts'][9999])-bound_high):
             spike=True
   return spike

def fill_df_six_sigma(dir, size, df, column_name, pos_shift, bound_low, bound_high):
   e = np.zeros((len(df)), dtype=bool)
   for i in range(size,len(df)):  # i position for moment in time for which we calculate array of outliers and do comparisson
        p_o = outlier(dir, df[i-size:i], column_name, pos_shift)
        for tm_pos in range(0,len(p_o)):   #check if some outlier is present in given bounds
               if (tm_(df['ts'][p_o[tm_pos][1]]) > tm_(df['ts'][i])-bound_low) and (tm_(df['ts'][p_o[tm_pos][1]]) < tm_(df['ts'][i])-bound_high):
                            e[i]='True'

   return e

def tm_(ts):
   return datetime.fromtimestamp(int(str(ts)[:-3]))



def calcSpread_1h(L04,L03,L02,L01,L1,L2,L3,L4, df,start):#creates columns with populated numpy array
   len_=len(df)
   e = np.zeros((len_)) #50 000
   for i in range(start, len_):
        begin=df['BTC_price'].loc[(df['ts']<df['ts'][i]+ 67280-3609676) & (df['ts']>df['ts'][i]-3609676)].mean()
        last=df['BTC_price'].loc[(df['ts']<df['ts'][i]) & (df['ts']>df['ts'][i]-67280)].mean()
        dif=last-begin
        if dif<L04:
           e[i] = '-4'
        if dif<L03:
           e[i] = '-3'
        if dif>L03 and dif<L02:
           e[i] = '-2'
        if dif>L02 and dif<L01:
           e[i] = '-1'

        if dif>L01 and dif<L1:
           e[i] = '0'

        if dif>L1 and dif<L2:
           e[i] = '1'
        if dif>L2 and dif<L3:
           e[i] = '2'
        if dif>L3:
           e[i] = '3'
        if dif>L4:
           e[i] = '4'
   return e


def calcSpread_11h(L03,L02,L01,L1,L2,L3, df, start):#creates columns with populated numpy array
   len_=len(df)
   e = np.zeros((len_)) #50 000
   for i in range(start, len_):
        begin=df['BTC_price'].loc[(df['ts']<df['ts'][i]+1039425-33542137) & (df['ts']>df['ts'][i]-33542137)].mean()
        last=df['BTC_price'].loc[(df['ts']<df['ts'][i]) & (df['ts']>df['ts'][i]-1039425)].mean()
        dif=last-begin
        if dif<L03:
           e[i] = '-3'
        if dif>L03 and dif<L02:
           e[i] = '-2'
        if dif>L02 and dif<L01:
           e[i] = '-1'

        if dif>L01 and dif<L1:
           e[i] = '0'

        if dif>L1 and dif<L2:
           e[i] = '1'
        if dif>L2 and dif<L3:
           e[i] = '2'
        if dif>L3:
           e[i] = '3'
   return e


def calcSpread_2h(delta, df,start):#creates columns with populated numpy array
   len_=len(df)
   e = np.zeros((len_)) #50 000
   for i in range(start, len_):
      begin=df['BTC_price'][i-2000:i].min()
      last=df['BTC_price'][i-2000:i].max()
      dif=last-begin
      if dif<delta:
         e[i] = True
   return e

def calcEMA(name,size, df):#creates columns with populated numpy array
   len_=len(df)
   e = np.zeros((len_)) #approximately 50 000
   for i in range(size, len_):
      e[i] = ewm(df[name][i-size:i])[i-1]
   return e

def ewm(df):
   return df.ewm(span=20,adjust=False,ignore_na=True).mean()
   
def calcMA(name,size, df):#name=currency, size=circle time(candles),df=dataframe name, len=hours to ananalyse
   len_=len(df)
   e = np.zeros((len_))
   for i in range(size,len_):
      e[i]=ma(df[name][i-size:i],500)[size-1]
   return e

def ma(df,n):
   return pd.DataFrame(df).rolling(n, center=True, min_periods=1).mean().to_numpy()


def combs(a):
    if len(a) == 0:
        return [[]]
    cs = []
    for c in combs(a[1:]):
        cs += [c, c+[a[0]]]
    return cs

def make_headers(headers):
   names=[]
   temp=''
   for i in range(0,len(headers)):
      if len(headers[i])>1:
         for j in range(0,len(headers[i])):
            if len(headers[i])>j+1:
               temp=temp+headers[i][j]+'│'
            else:
               temp=temp+headers[i][j]
      else:
         temp=headers[i][0]
      print(temp,'**')
      names.append(temp)
      print(len(headers[i]),'  -  ',i)
      temp=''
   return names

#FIND HOUR CANDLE
def det_hour_start(data):
    start_of_candle=0
    while c.second!=0 and c.minute!=0:
       c=datetime.fromtimestamp(int(str(d[i]['ts'])[:-3]))
       start_of_candle+=1
    return start_of_candle

#speed of price change
def populate_delta_array(data,name,pos_shift):
   return data[name]-data[name].shift(pos_shift)

def get_ucl(df):
   UCL= df.mean()+3* df.std()
   return UCL


def get_lcl(df):
   LCL = df.mean()-3* df.std()
   return LCL

def make_parameters():
   try:
      name='?'
      return()
   except:
      return('Nan')
#RECORD POSITION OF DELTA BASED ON MEDIAN


def get_velocity_outliers(df_):
   df_=df_
   oultiers_=[]
   lcl,ucl=get_limits(df_,1000,10)
   oultiers_=find_outlier_position(lcl,ucl,data_)
   origin=determine_interval(array)


def save(df_ar):
    folder = '/path/store3.h5'
    store = pd.HDFStore(folder)
    for i in range(0,len(df_ar)):
        name='df' + str(i)
        store[name]=df_ar[i]
        print('done saving ', i+1 , 'dataframe of parameters')



class order:
   def __init__(self):
      self.max=10000
      self.order_open_price = [0]*self.max
      self.open_time = [0]*self.max
      self.order_close_price = [0]*self.max
      self.close_time = [0]*self.max
      self.order_sl = [0]*self.max
      self.wage = [0]*self.max
      #SL increment
      #thred sleep parameter

class recollection:
   def  __init__(self, df, array_,cur_,cur2_,ts_array,ts):
      self.df_ = df
      self.array_ = array_
      self.cur_ = cur_
      self.cur2_ = cur2_
      self.ts_array_ = ts_array
      self.ts_ = 0 #PASS FIRST ELEMENT of data while initialisation
      self.df_.reset_index(drop = True, inplace = True)
      self.start = False
   def grow(self, cls, price, price2, ts):
      if ts>self.ts_:
         self.ts_ = ts
         self.ts_array_.append(ts)
         self.array_.append(price)
         self.df_ = cls.df_.shift(-1)
         self.df_[self.cur_].iloc[-1] = price #9999
         self.df_[self.cur2_].iloc[-1] = price2
         self.df_['ts'].iloc[-1] = ts
         self.df_.reset_index(drop = True, inplace = True)

def search_order_time(ord_time):
   array_ = []
   for i in range(0,len(ord_time)):
      if ord_time[i] > 0:
        array_.append(ord_time[i])
   return array_

def search_order_index(ar,df_):
   list_=[]
   for i in range(0,len(ar)):
      tmp=df_['ts'].loc[df_['ts']==ar[i]]
      list_.append(tmp.index[0])
   return list_

