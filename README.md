# sigmabot
cryptocurruency trading bot 
"Sigmatbot" or simply "Sigmabot" is a project aimed to trade based on a real time data.

## Getting Started

The purpose of this release is to demonstrate capabilities of the probabilistic approach 
in the field of analysis of a price action for trading.
Such algorithm can be used for the search of optimal entry point for trading for long or short positions or to red flag
opened positions during the price hikes.

### Key idea
Unlike parametric or conditional trading strategies for trading bots who use MA and RSI,
Sigmabot uses CLT(central limit theorem) or Six Sigma to define the function state in a real time.

Decision making in for such method is based on the solution of the disorder problem. 

Step by step algorithm is the following:
```
For each direction of the price action we detect abnormalities in speed rate.
Determine  the frequency the outlier occurrence for a given timeframe.
Based on the frequencies from upward and downward movement we produce frequency distribution table
Transform statistical data in a usable form by filtering conditional terms (predefined parameters) 
for the frequency distribution table, while satisfying definition consider we are at the end of a function price spike
otherwise the current point is not at the end of the price hike or no spikes has occurred for the frequency. 
We take the decision to buy, sell or stall(in case of a risk) solely by the definition of the present function.
Finally we record information for control and future analysis.
```

### Resutls

![big](https://user-images.githubusercontent.com/105378638/168127133-fec516ea-b691-4beb-8142-cd307b6b8d50.png)
The image shows the order point with the green dot and sell order with the red dot.
![bl](https://user-images.githubusercontent.com/105378638/168131764-a6e3222a-00bc-40c1-ab82-14925a027455.png)
The image demonstrates the selection of a spot at the bottom of the price drop with the green dot


```
30402 frequency up 39  down  198  price 128.14
30403 frequency up 39  down  199  price 128.04
30404 frequency up 39  down  200  price 127.49
30404 made order at lvl  127.49
outlies   outliers up:  39   down :  200
lvl:  127.49  SL increment:  2
 n lvl: 129.49
lvl:  129.49  SL increment:  1
 n lvl: 130.49
lvl:  130.49  SL increment:  1
 n lvl: 131.49
lvl:  131.49  SL increment:  1
 n lvl: 132.49
lvl:  132.49  SL increment:  1
 n lvl: 133.49
order closed in profit
lvl:  133.49 index_ 0
```
This is a daraft from a console. You may see the example of a program exectution.

## Deployment
This is a raw project and it might be complicated to start it on your machine.
There are 3 files, two of which works togeter and the downloader is separate from them.
You will need to have them both running. 
### Prerequisites
This program designed to run on the machine with python 3.8-3.10
You need to install libraries like numpy, pandas etc.

We need a historical(master) data. This specific program surves the purpose of data collection using REST Api.
Records BTC, LTC, MATIC price and ofcourse timestamp. Some other data for future research.

## Running the tests
First you need to search for some spesified rows in a program and configure 
the path to to your folder.
1) Check 'downloader.py'  file row 48 and put your path
2) put filename for a new '.csv' file in 'downloader.py' row 22
3) start  'downloader.py' it and give 14-20 hours to absorb enough information
4) run execute.py it will start to produce output in a console

