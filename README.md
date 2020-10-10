# Quantitative Trader

Welcome, in this Repo, you can fabricate, test, and produce customized trading algorithms and deploy them live in AWS.


![](readme%20photos/330.png)  ![](readme%20photos/aws.png) 

 
 ![](readme%20photos/Alpaca_Logo_yellow.jpg)

In this repo you will find a 2 main frameworks!

The first framework is the back testing framework, based on backtraders' infrastructure (https://www.backtrader.com) designed to back test your algorithms.
A critical component to any good algorithm is being able to back test but not over-fit the algorithm. This framework allows for the implementation of your algorithm within historical data based on past 
real time stock availability. 


![](readme%20photos/back_testing_module.png)


The live_trading framework allows for the implementation of your developed algorithm into real-time, by leveraging alpaca.markets commission free api.
Instantiating an AWS Ec-2, allows for the scheduling of algorithms using crontab to execute every weekday.


![](readme%20photos/logging.png)


If its is desired to run the program on a local host, the live graphing module can be ran separately for live indicator tracking and monitoring!


![](readme%20photos/live_graphing_module.png)


To get started see GETTING_STARTED.md

TO INSTALL ALL THE NECESSARY PACKAGES USE  

    pip install -r requirements.txt 




