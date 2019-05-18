import os, sys
import shutil
from datetime import datetime

from chart_generate import topn_requests_donut, yearoveryear_reqeusts_volume, delete_directory
from data_fetch import data as dframe
from tweet_generate import api, tweet


## create directory to store program logs
if not os.path.exists('logs'):
    os.mkdir('logs')
    
    
timestamp = datetime.now().strftime('%A %B %d,%Y   %I:%M%p')
module = sys.modules[__name__]
pprint_module_name = ((str(module).split('from')[1]).replace('>',''))

image_folder = os.path.join(os.pardir,'data','images')
image_files = []
image_files.append(yearoveryear_reqeusts_volume(dframe))    
for prd in ['year','week']:
    image_files.append(topn_requests_donut(dframe, period=prd))


def run_program():
    tweet(api_object=api, files=image_files, msg=timestamp)
    delete_directory(image_folder)
    shutil.move('execution.log',  os.path.join('logs','execution.log'))

    print('{} run sucessfully'.format(pprint_module_name))
    
    
## tweet charts & remove images folder after sent
if __name__ == "__main__":
    run_program()

    





