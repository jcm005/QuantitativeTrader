from pytz import timezone
import pytz
from datetime import datetime
import logging
import pandas as pd


class StreamTools:
    """
    Tools for the stream
    """

    def __init__(self):
        self.est = timezone('US/Eastern')

    @classmethod
    def time_converter(cls, some_time):
        """
        Convert date time object to a string
        """
        try:
            newtime = datetime.fromtimestamp(some_time / 1000)
            newtimes = newtime.strftime('%Y-%m-%d, %a, %H:%M')
            return newtimes
        except:
            logging.warning(some_time)

    @classmethod
    def check_time(cls):


        tz =timezone('US/Eastern')
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(tz)
        right_now = datetime.strftime(right_now, '%H:%M:%S')
        if int(right_now[0:2]) >= 16 or int(right_now[0:2]) <= 9:
            extended_hours = True
        else:
            extended_hours = False
        print(f'Extended hours are: {extended_hours}')
        return extended_hours

    @classmethod
    def stream_timer(cls):

        tz = timezone('US/Eastern')
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(tz)
        right_now = datetime.strftime(right_now, '%H:%M:%S')
        if int(right_now[0:2]) > 21 or int(right_now[0:2]) <= 7:
            extended_hours = True
        else:
            extended_hours = False
        return extended_hours

    def localize_time(self):
        """Default set to eastern time, when runnign on a virtual machine timezone may be off"""
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(self.est)
        right_now = datetime.strftime(right_now, '%H:%M:%S')

        return right_now

    @classmethod
    def export_pd(cls, data=pd.DataFrame()):

        data.to_csv(path='metrics.txt')

if __name__ == '__main__':

   # s = StreamTools()
   # time = s.localize_time()
   # print(time)

    pass