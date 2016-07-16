#----------------------------
# @FILE   : common.py
# @Author : ujnzxw
# @Date   : 2016-04-20
#---------------------------
import os
import re
import datetime
from lib.xtslog import xtslog
xtslog.init_logger("./logs/common.log")

'''@summary  : get the next specific number of date based on the week day num
   @Parameter: day_num - the number day of one week
   @Attention: Day    day_num
              ------------------
               Mon.      0
               Tue.      1
               Wed.      2
               Thr.      3
               Fri.      4
               For example, day_num=4 if you want to get the date of next firday.
               if today is friday, return today.

'''
def get_the_week_day(day_num):
    if not (0 <= day_num <= 4):
        xtslog.error("day_num must be [0, 4], day_num = %s"% day_num)
        return -1

    today = datetime.date.today()
    return today + datetime.timedelta( (day_num-today.weekday()) % 7 )

'''@summary  : get next even friday from today
   @Parameter: null
   @Attention: time zone is 'Asia/Shanghai'
'''
def get_next_even_friday():
    os.environ['TZ'] = 'Asia/Shanghai'
    today = datetime.date.today()
    # next firday upcoming
    # if today is friday, return today
    next_friday = today + datetime.timedelta( (4-today.weekday()) % 7 )
    week_num = next_friday.isocalendar()[1]
    if( week_num % 2 == 0): #even week
        return next_friday
    else:
        return (next_friday + datetime.timedelta(7))
'''@summary  : get next odd friday from today
   @Parameter: null
   @Attention: time zone is 'Asia/Shanghai'
'''
def get_next_odd_friday():
    os.environ['TZ'] = 'Asia/Shanghai'
    today = datetime.date.today()
    # next firday upcoming
    next_friday = today + datetime.timedelta( (4-today.weekday()) % 7 )
    week_num = next_friday.isocalendar()[1]
    if( week_num % 2 != 0): #odd week
        return next_friday
    else:
        return (next_friday + datetime.timedelta(7))
'''@summary  : get last even friday from today
   @Parameter: null
   @Attention: time zone is 'Asia/Shanghai'
'''
def get_last_even_friday():
    os.environ['TZ'] = 'Asia/Shanghai'
    today = datetime.date.today()
    # next firday upcoming
    next_friday = today + datetime.timedelta( (4-today.weekday()) % 7 )
    week_num = next_friday.isocalendar()[1]
    if( week_num % 2 == 0): #even week
        return (next_friday + datetime.timedelta(weeks=-2))
    else:
        return (next_friday + datetime.timedelta(weeks=-1))
'''@summary  : get last odd friday from today
   @Parameter: null
   @Attention: time zone is 'Asia/Shanghai'
'''
def get_last_odd_friday():
    os.environ['TZ'] = 'Asia/Shanghai'
    today = datetime.date.today()
    # next firday upcoming
    next_friday = today + datetime.timedelta( (4-today.weekday()) % 7 )
    week_num = next_friday.isocalendar()[1]
    if( week_num % 2 != 0): #odd week
        return (next_friday + datetime.timedelta(weeks=-2))
    else:
        return (next_friday + datetime.timedelta(weeks=-1))

'''@summary  : dalaba - get next publish date
   @Parameter: null
   @Attention: time zone is 'Asia/Shanghai'
'''
def get_next_publish_date():
    return get_next_odd_friday()

'''@summary  : dalaba - get last publish date
   @Parameter: null
   @Attention: time zone is 'Asia/Shanghai'
'''
def get_last_publish_date():
    return get_last_odd_friday()

