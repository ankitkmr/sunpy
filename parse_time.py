import pandas,sunpy,scipy
import numpy as np
import datetime,re
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse


TIME_FORMAT_LIST = [
    "%Y-%m-%dT%H:%M:%S.%f+%T",    # Example 2007-05-04T21:08:12.999999
    "%Y-%m-%dT%H:%M:%S.%f",    # Example 2007-05-04T21:08:12.999999
    "%Y/%m/%dT%H:%M:%S.%f",    # Example 2007/05/04T21:08:12.999999
    "%Y-%m-%dT%H:%M:%S.%fZ",   # Example 2007-05-04T21:08:12.999Z
    "%Y-%m-%dT%H:%M:%S",       # Example 2007-05-04T21:08:12
    "%Y/%m/%dT%H:%M:%S",       # Example 2007/05/04T21:08:12
    "%Y%m%dT%H%M%S.%f",        # Example 20070504T210812.999999
    "%Y%m%dT%H%M%S",           # Example 20070504T210812
    "%Y/%m/%d %H:%M:%S",       # Example 2007/05/04 21:08:12
    "%Y/%m/%d %H:%M",          # Example 2007/05/04 21:08
    "%Y/%m/%d %H:%M:%S.%f",    # Example 2007/05/04 21:08:12.999999
    "%Y-%m-%d %H:%M:%S.%f",    # Example 2007-05-04 21:08:12.999999
    "%Y-%m-%d %H:%M:%S",       # Example 2007-05-04 21:08:12
    "%Y-%m-%d %H:%M",          # Example 2007-05-04 21:08
    "%Y-%b-%d %H:%M:%S",       # Example 2007-May-04 21:08:12
    "%Y-%b-%d %H:%M",          # Example 2007-May-04 21:08
    "%Y-%b-%d",                # Example 2007-May-04
    "%Y-%m-%d",                # Example 2007-05-04
    "%Y/%m/%d",                # Example 2007/05/04
    "%d-%b-%Y",                # Example 04-May-2007
    "%Y%m%d_%H%M%S",           # Example 20070504_210812
    "%Y:%j:%H:%M:%S",          # Example 2012:124:21:08:12
    "%Y:%j:%H:%M:%S.%f",       # Example 2012:124:21:08:12.999999
    "%Y%m%d%H%M%S",            # Example 20140101000001 (JSOC / VSO)
]

REGEX = {
    '%T': '(?P<timezone>\d{4})',
    '%Y': '(?P<year>\d{4})',
    '%j': '(?P<dayofyear>\d{3})',
    '%m': '(?P<month>\d{1,2})',
    '%d': '(?P<day>\d{1,2})',
    '%H': '(?P<hour>\d{1,2})',
    '%M': '(?P<minute>\d{1,2})',
    '%S': '(?P<second>\d{1,2})',
    '%f': '(?P<microsecond>\d+)',
    '%b': '(?P<month_str>[a-zA-Z]+)',
}

def _regex_parse_time(inp, format):
    # Parser for finding out the minute value so we can adjust the string
    # from 24:00:00 to 00:00:00 the next day because strptime does not
    # understand the former.
    for key, value in REGEX.iteritems():
        format = format.replace(key, value)
    match = re.match(format, inp)
    if match is None:
        return None, None
    try:
        hour = match.group("hour")
    except IndexError:
        return inp, timedelta(days=0)
    if match.group("hour") == "24":
        if not all(_n_or_eq(_group_or_none(match, g, int), 00)
            for g in ["minute", "second", "microsecond"]
        ):
            raise ValueError
        from_, to = match.span("hour")
        return inp[:from_] + "00" + inp[to:], timedelta(days=1)
    return inp, timedelta(days=0)

def parse_time(time_string, time_format=''):
    """Given a time string will parse and return a datetime object.
    Similar to the anytim function in IDL.
    utime -- Time since epoch 1 Jan 1979

    Parameters
    ----------
    time_string : [ int, float, time_string, datetime ]
        Date to parse which can be either time_string, int, datetime object.
    time_format : [ basestring, utime, datetime ]
        Specifies the format user has provided the time_string in.

    Returns
    -------
    out : datetime
        DateTime corresponding to input date string

    Note:
    If time_string is an instance of float, then it is assumed to be in utime format.

    Examples
    --------
    >>> sunpy.time.parse_time('2012/08/01')
    >>> sunpy.time.parse_time('2005-08-04T00:01:02.000Z')

    """
    if isinstance(time_string, pandas.tslib.Timestamp):
    	return time_string.to_datetime()
    elif isinstance(time_string, datetime) or time_format == 'datetime':
        return time_string
    elif isinstance(time_string, tuple):
        return datetime(*time_string)
    elif time_format == 'utime' or  isinstance(time_string, (int, float))  :
        return datetime(1979, 1, 1) + timedelta(0, time_string)
    elif isinstance(time_string, pandas.tseries.index.DatetimeIndex):
    	return time_string._mpl_repr()
    elif isinstance(time_string, np.ndarray) and 'datetime64' in str(time_string.dtype):
        ii = [ss.astype(datetime) for ss in time_string]
        # Validate (in an agnostic way) that we are getting a datetime rather than a date
        return np.array([datetime(*(dt.timetuple()[:6])) for dt in ii])
    elif time_string is 'now':
        return datetime.utcnow()
    else:
        # remove trailing zeros and the final dot to allow any
        # number of zeros. This solves issue #289
        if '.' in time_string and '+' not in time_string:
            time_string = time_string.rstrip("0").rstrip(".")

        if '+' in time_string :
            time_zone = time_string[time_string.rindex('+'):]
            time_string_strip = time_string[:time_string.rindex('+')].rstrip("0").rstrip(".")
            d = parse(time_string_strip + "UTC" + time_zone)
            return d
        elif '-' in time_string :
            time_zone = time_string[time_string.rindex('-'):]
            time_string_strip = time_string[:time_string.rindex('-')].rstrip("0").rstrip(".")
            d = parse(time_string_strip + "UTC" + time_zone)

        #     d = datetime.strptime(time_string_strip, "%Y-%m-%dT%H:%M:%S.%f")
        #     d = pytz.timezone(time_zone).localize(d)
            return d
        for time_format in TIME_FORMAT_LIST:
            try:
                try:
                    ts, time_delta = _regex_parse_time(time_string,
                                                       time_format)
                except TypeError:
                    break
                if ts is None:
                    continue
                return datetime.strptime(ts, time_format) + time_delta
            except ValueError:
                pass
        raise ValueError("{tstr!s} is not a valid time string!".format(tstr=time_string))


print type(parse_time('2015-03-18T12:49:22.979471000+0000'))
print parse_time('2015-03-18T12:49:22.979471000+0000')
