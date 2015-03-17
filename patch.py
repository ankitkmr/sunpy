import pandas as pd
import pytz
import datetime
import numpy as np
from tzlocal import get_localzone

# this is just a way around through the same example as given in the issue

tz = get_localzone()
from sunpy.time import parse_time

x=np.linspace(0,19,20)
basetime=datetime.datetime.utcnow()
times=[]  

for thing in x:
	times.append(basetime + datetime.timedelta(0,thing))

times = pd.to_datetime(times)			#Change DONE HERE

#print "\n \n \n ======== \n"

test_pandas=pd.DataFrame(np.random.random(20),index=times)

print test_pandas

utc = pytz.timezone('UTC')					#Change DONE HERE
test_pandas.index = times.tz_localize(tz).tz_convert(utc)	#Change DONE HERE

print "\n \n \n ======== \n"

print test_pandas


# print type(pd.to_datetime(str(test_pandas.index.values[0])).strftime('%Y.%m.%d'))
# print pd.to_datetime(str(test_pandas.index.values[0])).strftime('%Y.%m.%d')
print parse_time(pd.to_datetime(str(test_pandas.index.values[0])).strftime('%Y/%m/%d') )	#Change DONE HERE

#parse_time(...) now works fine
