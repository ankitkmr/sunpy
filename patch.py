import pandas as pd
import pytz
import datetime
import numpy as np
from pytz import reference

# this is just a way around through the same example as given in the issue

today = datetime.datetime.now()
localtime = reference.LocalTimezone()

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
test_pandas.index = times.tz_localize(localtime.tzname(today)).tz_convert(utc)	#Change DONE HERE  #now using pytz

print "\n \n \n ======== \n"

print test_pandas


# print type(pd.to_datetime(str(test_pandas.index.values[0])).strftime('%Y.%m.%d'))
# print pd.to_datetime(str(test_pandas.index.values[0])).strftime('%Y.%m.%d')
print parse_time(pd.to_datetime(str(test_pandas.index.values[0])).strftime('%Y/%m/%d') )	#Change DONE HERE

#need to add support for numpy.datetime64 instances like '2015-03-18T12:49:22.979471000+0000' before using __str__() to parse them

'''@dpshelio 
Ok about the first issue that it takes away timezone can you explain how I register timezone? I kinda dont know this new format '%Y': '(?P\d{4})', 
the above happens because if you see parse_time source code then at the else condition in the end of its function definition http://docs.sunpy.org/en/latest/_modules/sunpy/time/time.html#parse_time
else:
	if '.' in time_string:
		time_string = time_string.rstrip("0").rstrip(".")

needs to be made 
else:
	if '.' in time_string and '+' not in time_string:
		time_string = time_string.rstrip("0").rstrip(".")
		
moreover the way time_string in our case is formatted is not supported in the TIME_FORMAT_LIST and REGEX (lists defined in source code for parse_time)

So I can add that support but I kinda dont know how to register for the 000 in the end of +000 like

'%T': '(?P\d{4})',  #in the REGEX list in source code

# Assuming I replace T for end 000 what goes after colon. Need some help here
'''
