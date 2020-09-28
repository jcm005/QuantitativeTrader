#Note 

This framework is under going a reconstruction, to become more SOLID principled, implementing Factory Methods and other Design patterns, The newest updated scripts can be found in the oop folder


# Live_trading

In this repo, you can code your algorithm with the same principles as back_testing to trade in real_time.

One of the first things I should mention is the only pitfall to this program is occasional disconnection from wifi. 
I have taken precautions for the program to automatically re-establish a connection if the websocket connection has failed.

to get started with this program it is best by running the command

    python3 stream2.py
    
in terminal. 


The program will then obtain a connection with alpacas live streaming api. This program can recieve second based updates of stock information, however it is currently using a data aggregation technique to deliver updates every minute.

Every time the programs is executed there are three log files created. 

    log.txt
    
    stream2.txt
    
    candle.txt
    
log.txt provides the time of every connection made with websockets this gives insight to when the program may have failed, and automatically re-established a connection

candle.txt provides the data obtain from the api formated in a friendly OHLC format with the ability of adding custom indicators.

stream2.txt relays the step by step processes the program takes in the strategy/algorithm, logging wether a buy or sell was tried, failed, or executed. 


A great feature of this repo is the live_graphing feature.
By executing live_graphing.py, the program will use the dash module to produce an html with a live rendering of the information in candle.txt
this program can be modified to watch the graphing of your favorite indicators in real time, giving insightful knowledge on algorithm optimization. 
Please do note stream2.py must be running in order to use the live graphing. An update to merge these two to run coincidentally is under way.