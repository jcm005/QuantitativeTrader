from  datetime import datetime

right_now = datetime.now()
right_now = datetime.strftime(right_now,'%H:%M:%S')

if 9 < int(right_now[:2]) < 19:
    print('back in action')
else:
    print('out of order')

def check_time():
    right_now = datetime.datetime.now()
    right_now = datetime.datetime.strftime(right_now, '%H:%M:%S')
    if 9 < int(right_now[:2]) < 17:
        print('back in action')
    else:
        print('out of order')