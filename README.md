# Trader

Welcome, in this Repo, you will find two series of frameworks. Live_trading 
and Back_Testing framework.

The Back_Testing platform is based on backtraders' infrastructure https://www.backtrader.com
which receives historical stock data with variables declared in test.py . It is named test.py because it is the primary platform that strategies can be built on.

The Live_Trading repository allows for the implementation of your developed algorithm into real-time.

TO INSTALL ALL THE NECESSARY PACKAGES USE  

    pip install -r requirements.txt 


To see more information check out the following directories.

To use this repository to trade you need to make an account using the broker https://alpaca.markets, once you set yourself up you should have an

    API_KEY & SECRET_KEY
    
Then create a keys.py file for the back_trading repo. In the format of

    API_KEY = 'Enter your key in here'
    PAPER_API = 'Enter your paper key in here'
    SECRET_KEY = 'Enter your secret key in here'
    