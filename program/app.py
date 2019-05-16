from datetime import datetime
from chart_generate import topn_requests_donut, yearoveryear_reqeusts_volume
from data_fetch import data as dframe
from tweet_generate import api, tweet

timestamp = datetime.now().strftime('%A %B %d,%Y   %I:%M%p')

image_files = []
for prd in ['year','week']:
    image_files.append(topn_requests_donut(dframe, period=prd))
    image_files.append(yearoveryear_reqeusts_volume(dframe))
    tweet(api_object=api, files=image_files, msg=timestamp)
