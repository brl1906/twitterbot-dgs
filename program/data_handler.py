"""Module with collection of helpful functions for fetching and preparing the
data for the DGS twitterbot program that automates the tweets of key performance
observations or charts related to events in facility mainteance and repair
division.
Author: Babila Lima
Date 3/3/2019
"""

from configparser import ConfigParser
import datetime as dt
import os
import warnings

import datadotworld as dw
import pandas as pd

warnings.filterwarnings('ignore')

config = ConfigParser() # accessing datadotworld variables
config.read(os.path.join(os.pardir,'configuration','config.ini'))
folder = config.get(section='data_files', option='directory')
file = config.get(section='data_files',option='geo_file')

def get_data(key, data_name):
    """
    Return datadotworld dataset as pandas dataframe.

    Parameters
    ----------
    key:        str
        Dataset key for target data.world dataset.

    data_name:  str
        Name of the data.world dataset or value associated with the key

    Returns
    -------
    pandas dataframe

    Examples
    --------
    >>> load_data(key='org/division', data_name='employee_history')
    """
    data_obj = dw.load_dataset(dataset_key=key, auto_update=True)
    data = data_obj.dataframes[data_name]

    return data


def clean_data(frame):
    """Prepare dataset for analysis.

    Parameters
    ----------
    frame:        pandas dataframe object
        Dataframe object of raw data from datadotworld.

    Returns
    -------
    pandas dataframe

    Examples
    --------
    >>> clean_data(frame=data)
    """

    columns = ['bl_id', 'completed_by','cost_labor','cost_other',
           'cost_parts', 'cost_total','date_assigned','date_closed',
           'date_completed', 'date_requested','dv_id', 'location',
           'prob_type','site_id','time_completed','time_requested',
           'wo_id', 'work_team_id','time_start','time_end']

    date_conversion_cols = ['date_assigned','date_closed','date_completed',
                            'date_requested']
    time_conversion_cols = ['time_completed','time_start','time_end',
                            'time_requested']

    def format_dates(df, cols):
        """Convert date columns to pandas datetime series and shorten column name."""
        drop_cols = []
        for col in cols:
            if col in df.columns:
                df[col.split('_')[-1]] = pd.to_datetime(df[col])
                drop_cols.append(col)
            else:
                print('"{}" column not found in dataframe'.format(col))
        df.drop(drop_cols, axis=1, inplace=True) # delete original columns after conversion


    def format_times(df, cols):
        """Convert time columns to date time objects replacing date with
        generic 1899-12-31."""

        timestamp_1899 = lambda x: x.replace(year=1899, month=12, day=31)
        for col in cols:
            if col in df.columns:
                df[col] = (pd.to_datetime(df[col])
                          .apply(timestamp_1899))
            else:
                print('"{}" column not found in dataframe.'.format(col))

    # filter for target columns & eliminate Tests
    dataframe = frame[columns][(frame[columns]['prob_type'] != 'TEST(DO NOT USE)')]

    dataframe['wo_id'] = dataframe['wo_id'].astype(str) # convert workorder from float to str
    format_dates(df=dataframe, cols=date_conversion_cols) # format timestamp data
    format_times(df=dataframe, cols=time_conversion_cols)
    dataframe.set_index('requested', inplace=True)
    dataframe.sort_index(inplace=True)
    dataframe['duration'] = [drtn.days for drtn in dataframe['completed'] - dataframe.index]
    # remove data from initial (partial) year of Archibus
    dataframe = dataframe[(dataframe.index.year != 2013)]
    dataframe['year'] = dataframe.index.year

    # add volumne of requests by problem type by (request) year
    dataframe['yrly_rqst_volume'] = dataframe.groupby([dataframe.index.year,'prob_type'])['wo_id'].transform('count')
    dataframe['year_completed'] = [date.year for date in dataframe['completed']]
    dataframe['prblmtype_avg_yrly_drtn'] = dataframe.groupby(['year','prob_type'])['duration'].transform('mean')
    dataframe['prblmtype_yrly_rqsts'] = dataframe.groupby(['year','prob_type'])['wo_id'].transform('count')
    dataframe['bld_yrly_rqsts'] = dataframe.groupby(['year','bl_id'])['wo_id'].transform('count')
    dataframe['bld_avg_yrly_drtn'] = dataframe.groupby(['year','bl_id'])['duration'].transform('mean')

    return dataframe


def add_latlong(frame, file, nrows2skip):
    """Add latitude and longitude data to dataframe from file.
    Parameters
    ----------
    frame       :   pandas dataframe
        pandas dataframe object returned from clean_data function

    file        :   str
        name of file containing lat long for buildings to add this
        information to the dataframe for generating map visualsself.

    nrows2skip  :   int
        number of rows to skip when reading the lat_long_file

    Returns
    -------
    pandas dataframe

    Examples
    --------
    >>> add_latlong(frame=df, file=your_file, nrows2skip=10)
    """
    lat_long_dataframe = pd.read_excel(file, skiprows=nrows2skip)
    lat_long_dataframe.columns = ['bl_id','name','addr','site_id','latitude','longitude']

    geo_dict = {}
    for bld in lat_long_dataframe['bl_id'].unique():
        geo_dict[bld] = {'latitude': lat_long_dataframe.loc[lat_long_dataframe['bl_id'] == bld]['latitude'].values[0],
                        'longitude': lat_long_dataframe.loc[lat_long_dataframe['bl_id'] == bld]['longitude'].values[0],
                        'bld_name': lat_long_dataframe.loc[lat_long_dataframe['bl_id'] == bld]['name'].values[0]}

    frame['latitude'] = frame['bl_id'].apply(lambda x: geo_dict[x]['latitude'])
    frame['longitude'] = frame['bl_id'].apply(lambda x: geo_dict[x]['longitude'])
    frame['bld_name'] = frame['bl_id'].apply(lambda x: geo_dict[x]['bld_name'])

    return frame


def weekday_name(integer):
    """Convert integer from tiemstamp dayofweek value to weekday name.

    Parameters
    ----------
    inetger:  int
        integer returned from dayofweek value in a timestamp object

    Returns
    -------
    string of the week day name

    Examples
    -------
    >>> weekday_name(0)
    """
    day_names = ("Monday","Tuesday","Wednesday","Thursday","Friday",
                "Saturday","Sunday")

    return day_names[integer]


def dataframe(key,data_name,lat_long_file,skiprows):
    """Return ready dataframe for twitterbot, cleaned and features added.

    Parameters
    ----------
    key             :   str
        Dataset key for target data.world dataset.

    data_name       :   str
        Name of the data.world dataset or value associated with the key

    lat_long_file   :   str
        filename of file containing lat long for buildings to add this
        information to the dataframe for generating map visualsself.

    skiprows        :   int
        number of rows to skip when reading the lat_long_file

    Returns
    -------
    pandas dataframe

    Examples
    -------
    >>> dataframe(key=your_key, data_name=target_data,
                  lat_long_file=filename, skiprows=5)
    """
    try:
        data = get_data(key=key,data_name=data_name)
    except Exception as e:
        print(e)
    try:
        cleaned_data = clean_data(frame=data)
    except Exception as e:
        print(e)
    try:
        dframe = add_latlong(frame=cleaned_data,file=lat_long_file,
                    nrows2skip=skiprows)
    except Exception as e:
        print(e)

    return dframe


def strong_correlations(df, col_name, threshold=.5):
    """Show summary of features with a +.5 or greater correlation.

    Parameters
    ----------
    df          :  pandas dataframe
        dataframe that is cleaned, features added and ready for use in project.

    col_name    :  str
        target column name in dataframe for against which correlations of the
        other numerical data is sought

    threshold   : float (default is 0.5)
        absolute value limit for which correlations above .5 or -.5 should be
        returned if features in dataframe exists with this level of correlation


    Returns
    -------
    string with sentence in dicating how many and which features have a
    correlation with the target column above .5 or below -.5 if the default
    argument is not changed or else, above or below the value passed to the
    threshold paramter.

    Examples
    -------
    >>> strong_correlations(dframe, 'on_time', threshold=0.3)
    """

    features = []
    num_strong = abs(df.corr()[col_name] >=threshold).sum() - 1
    feature_list = df.corr()[col_name][abs(df.corr()[col_name]) >=threshold].index.tolist()

    for ftr in feature_list:
        if ftr != col_name:
            features.append(ftr)

    summary = 'In the data, {} variable(s) is strongly correlated with "{}": {}'.format(
                num_strong, col_name, [i for i in features])

    return summary


data = dataframe(key=config.get(section='datadotworld', option='key'),
                data_name=config.get(section='datadotworld', option='data_name'),
                lat_long_file=os.path.join(os.pardir,folder,file), skiprows=6)
