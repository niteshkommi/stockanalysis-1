from alpha_vantage.timeseries import TimeSeries
from pprint import pprint
ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
data, meta_data = ts.get_intraday(
    symbol='GOOGL', interval='day', outputsize='full')
pprint(data.head(20))