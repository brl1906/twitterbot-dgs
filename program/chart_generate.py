"""Module for generating charts and saving to file as png to produce the objects
to be passed as images to tweet.
Author: Babila Lima
Date 3/3/2019
"""
import os
from datetime import datetime

import matplotlib.colors
import matplotlib.cm as colormap
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_style(style='ticks')

## donut chart of request volume by problem type
## visualize the top n problem types by category 
## with options for viewing top n this week vs this year
def topn_requests_donut(df, period, topn=20):
    """Create donut chart of top 20 problem types by reqeust volume.

    Parameters
    ----------
    df:       pandas dataframe
        final datafame containing data for generating tweets

    topn:     int
        number of problem types to return in search. the top n number
        of most frequent problem types by request volume.

    period:   str
        timeframe for piechart. Sets data filter to current year only
        or current week.  Options include 'year' (default) and 'week'.

    Returns
    -------
    String: filename of chart image.

    Examples
    --------
    >>> topn_requests_donut(df=dataframe, period='year')

    >>> topn_requests_donut(df=dataframe, period='week', topn=10)

    """
    current_year = datetime.today().strftime('%Y')
    current_week = datetime.today().strftime('%W')

    if period == 'year':
        dframe = df[(df['prob_type'] != 'OTHER') &
                    (df['year'] == int(current_year))]

    elif period == 'week':
        dframe = df[(df['prob_type'] != 'OTHER') &
                (df['year'] == int(current_year)) &
                (df.index.week >= int(current_week) - 2)]
    else:
        # pass condition generates error forcing 'year' or 'week' as arguments
        pass

    labels = dframe['prob_type'].value_counts().head(topn).index
    values = dframe['prob_type'].value_counts().head(topn).values
    cmap = plt.cm.summer_r  # set colorscale for chart

    ## set a default max and min value to 
    ## prevent an 'empty sequence error'
    minimum = min(values, default=0)
    maximum = max(values, default=0)
    normalize_color = matplotlib.colors.Normalize(vmin=minimum,vmax=maximum)
    colors = [cmap(normalize_color(val)) for val in values]
    
    ## create donut chart figure
    plt.figure(figsize=(7,7))
    circle = plt.Circle((0,0), .55, color='white')
    plt.pie(x=values, labels=labels, colors=colors,
            wedgeprops={'linewidth':6}, textprops={'color':'green'})
    pie = plt.gcf()
    pie.gca().add_artist(circle)

    if period == 'year':
        title_object = plt.title('Top {} Maintenance Requests\nCalendar Year: {}'
                        .format(topn, current_year))
    elif period == 'week':
        title_object =  plt.title('Top {} Maintenance Requests\nLast 2 Weeks'
                        .format(topn))
    else:
        pass

    ## set chart title properties -- styling
    plt.setp(title_object, color='green')
    plt.setp(title_object, fontfamily='monospace')
    plt.setp(title_object, fontsize='x-large')
    plt.setp(title_object, fontweight='bold')

    ## save chart image and return png file
    stamp = datetime.today().strftime('%m-%d-%Y')
    if not os.path.exists(os.path.join(os.pardir,'data','images')):
        os.mkdir(os.path.join(os.pardir,'data','images'))

    if period == 'year':
        base_fname = ('{} top{}_requests{}.png'
                        .format(stamp,topn,current_year))
    elif period == 'week':
        base_fname = ('{} top{}_requests_week{}.png'
                        .format(stamp,topn,current_week))
    else:
        pass

    full_fname = os.path.join(os.pardir,'data','images', base_fname)
    image = pie.savefig(fname=full_fname)

    return full_fname


## bar & line graph providing a point in time comparison
## of weekly maintenance reqeust volume and helps to 
## visualize answers to the question: 'this time last year vs 
## right now how many more or less request did we have?' 
def yearoveryear_reqeusts_volume(df):
    """
    Create chart with 2 traces showing year over year comparison of weekly
    work requests for current (line chart) and previous year (bars).

    Parameters
    ----------
    df:       pandas dataframe
        final datafame containing data for generating tweets


    Returns
    -------
    String: filename of chart image.

    Examples
    --------
    >>> yearoveryear_reqeusts_volume(df=dataframe)

    """
    
    current_year = int(datetime.today().strftime('%Y'))
    last_year = current_year - 1
    runtime_stamp = datetime.today().strftime('%m-%d-%Y')

    current_year_data = (df[df['year'] == current_year]
                         .groupby(df[df['year'] == current_year].index.week)
                         ['wo_id'].count())
    last_year_data = (df[df['year'] == last_year]
                      .groupby(df[df['year'] == last_year].index.week)
                      ['wo_id'].count())

    densely_dashdot_linestyle = (0, (3, 1, 1, 1, 1, 1))
    fig, ax = plt.subplots(figsize=(11,6))

    ## plot current year data as line chart to visualize
    ## the number of request per week through 
    ## the current week at run time
    current_year_data.plot(color='#31a354',linewidth=3.5,
                           linestyle=densely_dashdot_linestyle,
                           label=current_year);

    ## plot the last year data of requests per week as bar
    ## chart to communicate the workload last year and provide
    ## easy visual comparison for point in time request workload
    last_year_data.plot(kind='bar', color='#a1d99b',width=.5, label=last_year)

    sns.despine(offset=10,)
    plt.xlabel('52 weeks of calendar year')
    plt.ylabel('work requests (per week)')
    ax.get_xaxis().set_ticks([]) # remove xaxis tick labels
    plt.title('Maintenance Work Request Volume\nThrough {} ({} vs {})'.
              format(runtime_stamp, last_year, current_year),
             fontname='monospace', fontsize='x-large')
    
    ## set legend in single row along xaxis
    plt.legend(bbox_to_anchor=(0,-.095), loc='lower left',
          ncol=2, frameon=False);

    
    ## create a data/images folder if one doesn't exist
    ## save the chart image to images folder 
    if not os.path.exists(os.path.join(os.pardir,'data','images')):
        os.mkdir(os.path.join(os.pardir,'data','images'))

    base_fname = ('{} weekly_volume_comparision.png'.format(runtime_stamp))
    full_fname = os.path.join(os.pardir, 'data','images', base_fname)
    fig.savefig(full_fname)
    
    return full_fname