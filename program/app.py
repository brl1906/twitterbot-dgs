import os
from datetime import datetime

from chart_generate import topn_requests_donut, yearoveryear_reqeusts_volume, delete_directory
from data_fetch import data as dframe
from tweet_generate import api, tweet

timestamp = datetime.now().strftime('%A %B %d,%Y   %I:%M%p')

image_folder = os.path.join(os.pardir,'data','images')
image_files = []
image_files.append(yearoveryear_reqeusts_volume(dframe))    
for prd in ['year','week']:
    image_files.append(topn_requests_donut(dframe, period=prd))
    
    
## tweet charts & remove images folder after sent
if __name__ == "__main__":
    tweet(api_object=api, files=image_files, msg=timestamp)
    delete_directory(image_folder)

    





