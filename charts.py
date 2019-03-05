"""Module for generating charts and saving to file as png to produce the objects
to be passed as images to tweet.
Author: Babila Lima
Date 3/3/2019
"""

from datetime import datetime
import os

import data_handler
import matplotlib.colors
import matplotlib.cm as colormap
import matplotlib.pyplot as plt
import plotly.io as pio
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as pyo
import seaborn as sns

pyo.init_notebook_mode(connected=True)
sns.set_style(style='ticks')
# set matplotlib backend for Mac Os X system
#matplotlib.use('TkAgg')

dataframe = data_handler.data

# first chart -- donut chart of request volume by problem type
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
        or current week.  Options include 'year' (default) and 'weeks'.

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
    minimum, maximum = min(values), max(values)
    normalize_color = matplotlib.colors.Normalize(vmin=minimum,vmax=maximum)
    colors = [cmap(normalize_color(val)) for val in values]
    # chart
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

    # set chart title properties -- styling
    plt.setp(title_object, color='green')
    plt.setp(title_object, fontfamily='monospace')
    plt.setp(title_object, fontsize='x-large')
    plt.setp(title_object, fontweight='bold')

    # save and return png file
    stamp = datetime.today().strftime('%m-%d-%Y')
    if not os.path.exists('images'):
        os.mkdir('images')

    if period == 'year':
        img_filename = ('images/{} top{}_requests{}.png'
                        .format(stamp,topn,current_year))
    elif period == 'week':
        img_filename = ('images/{} top{}_requests_week{}.png'
                        .format(stamp,topn,current_week))
    else:
        pass
    image = pie.savefig(fname=img_filename)

    return img_filename

# second chart -- comparison of weekly maintenance reqeust volume
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
    current_year = datetime.today().strftime('%Y')
    stamp = datetime.today().strftime('%m-%d-%Y')
    dfs_dict = {}
    traces = []
    for i, yr in enumerate([int(current_year)-1, int(current_year)]):
        dfs_dict[str(yr)] = df[(df['year'] == yr)]

        # set last year to bar chart
        if i == 0:
            traces.append(go.Bar(
                x = (dfs_dict[str(yr)].groupby(dfs_dict[str(yr)]
                                               .index.week)['wo_id'].count().index),
                y = (dfs_dict[str(yr)].groupby(dfs_dict[str(yr)]
                                               .index.week)['wo_id'].count().values),
                name = yr,
                marker = {'color':'#bdbdbd'}))

        # set current year to line chart
        else:
            traces.append(go.Scatter(
                x = (dfs_dict[str(yr)].groupby(dfs_dict[str(yr)]
                                               .index.week)['wo_id'].count().index),
                y = (dfs_dict[str(yr)].groupby(dfs_dict[str(yr)]
                                               .index.week)['wo_id'].count().values),
                name = yr,
                line = {'color':'#636363'}))


    layout = go.Layout(
        title = ('<b>Weekly Maintenance Reqeust Volume<br>Through {} ({} vs {})</b>'
                 .format(datetime.today().strftime('%m-%d-%Y'),
                         int(current_year) -1,current_year)),
        font = {'family':'monospace'},
        xaxis = {
            'showgrid':False,
            'zeroline':False,
            'range':[0,52],
            'title':'week of year'},
        yaxis = {
            'showgrid':False,
            'zeroline':False,
            'range':[100,500],
            'title':'work requests<br>weekly'},
        legend = {'orientation':'h'}
                    )

    fig = {'data':traces, 'layout':layout}
    # save image to file
    if not os.path.exists('images'):
        os.mkdir('images')

    img_filename = ('images/{} weekly_volume_comparision.png'.format(stamp))
    pio.write_image(fig=fig, file=img_filename, format='png')

    return img_filename
