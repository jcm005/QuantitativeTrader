# Back_Testing

If you do not yet have a trading account opened with alpaca.markets, please create one to be able to use this framework.
Once that is established, you should have obtained an

    API_KEY & SECRET_KEY
    
These keys need to be protected, for they are the access point to your money. Insert these keys 
in a keys.py file for this repo. In the format of

    API_KEY = 'Enter your key in here'
    PAPER_API = 'Enter your paper key in here'
    SECRET_KEY = 'Enter your secret key in here'
    
You can find the PAPER_API key by switching to the paper trading account on the left menu bar.

After establishing your account and keys, you can start testing. The platform is straightforward to get started right away. By default, the algorithm currently loaded in the program is an algorithm based on a specific stock 'TSLA' and is aimed to exploit the stock volatility for about a 10% rate of return.
The framework is currently being worked on to allow the plug and play of modules as algorthims for a simple design.

By changing these variables,

    asset = ['TSLA']
    start_date = '2020-05-01'           # ticker symbols to be tested
    time_interval = 'minute'            # collect data per each ---
    time_delt = 7
    time_period =6 
    
You can test and grab any historical data for a desired stock and date.

The time interval has three options, 'minute', 'hour' or 'day'.
The (time delt * the time period)  gives you the total amount of days your historical data will aggregate data for.
The time delt is simply the 'how many days' the datagrabber.py file will grab at a time, keeping this value at 7 days prevents the loss of data in the pipeline. So by simply setting the time period to the number of weeks for your testing period ensures no data is lost or corrupted. 

At the moment, the best way to create an algorithm is by going to the next() function in the class that's being passed as a strategy and developing the logic for your algorithm there.

The frameworks awaits a massive update to practice more 'SOLID' principles of programming



