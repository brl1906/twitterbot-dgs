"""Module for functions handling the generation of tweets.
Author: Babila Lima
Date 3/4/2019
"""

from configparser import ConfigParser
import imghdr
import os
import sys

import tweepy

config = ConfigParser()
config.read(os.path.join(os.pardir,'configuration','config.ini'))
#config.read('configuration/config.ini')
api_key = config.get(section='api_key', option='api_key')
api_secret = config.get(section='api_secret', option='api_secret')
access_token = config.get('access_token', 'access_token')
token_secret = config.get('token_secret', 'token_secret')
# instantiate api object
auth = tweepy.OAuthHandler(consumer_key=api_key, consumer_secret=api_secret)
auth.set_access_token(key=access_token, secret=token_secret)
api = tweepy.API(auth)

# twitter geo-tagging parameters is ignored if (the default) geo_enabled is false
abelwolman_location = {'latitude':39.291664, 'longitude':-76.610726}

def get_media_ids(tweepy_api, img_files):
    """Generate list of twitter media_ids for images to include in post method for tweets.

    Parameters
    ----------
    tweepy_api : tweepy.api.API
        A tweepy api object resulting from initializing, oauth with twitter api keys

    img_files  : list
        List of image files to be included in tweet if tweet is to have
        a picture associated with it. Files must be jpeg or png to comply with the
        'simple image upload' method in the current Twitter API.

    Returns
    -------
    dict
        dict of response objects for each uploaded image file that includes
        attributes below:
        {
        "media_id": 710511363345354753,
        "media_id_string": "710511363345354753",
        "size": 11065,
        "expires_after_secs": 86400,
        "image": {
            "image_type": "image/jpeg",
            "w": 800,
            "h": 320
                }
        }

    Examples
    --------
    >>> get_media_ids(tweepy_api=api_object, img_files=['img1.png','img2.jpeg'])

    """
    # add future feature to force size compliance
    #media_megabyte_limits = {'image':5,'GIF':15,'video':15}
    media_id_responses = {}
    errors = []
    for file in img_files:
        # force compliance with twitter api by removing bad filetypes before request
        if imghdr.what(file) == 'jpeg' or imghdr.what(file) == 'png':
            try:
                twitter_api_media_response = (tweepy_api.media_upload(
                    filename = file,
                    additional_owners = None))

                # store media id and filetype in dictionary
                media_id_responses[file] = {
                    'media_id': twitter_api_media_response.media_id,
                    'file_kilobytes': twitter_api_media_response.size}

            except tweepy.TweepError as Te:
                errors.append(Te)

    return (media_id_responses
            if len(media_id_responses) > 0
            else
            errors)

def post_tweet(tweepy_api, message, media_objects={}, latitude=39.291664,longitude=-76.610726):
    """Posts tweet for a given status and returns result of attempt.

    Parameters
    ----------
    tweepy_api      : tweepy.api.API
        A tweepy api object resulting from initializing oauth with Twitter api
        keys

    message         : str
        The text to be posted in the body of the tweet. Optionally, users can
        pass a function if the return of the function is a string.  For example,
        if a function my_message() returns a string, my_message() can be passed
        to the message parameter of the function.

    media_objects  : dict
        A dictionary for which the keys are the list of jpeg or png files to be
        included in tweet and, for which the values are: 1) the media_id which
        Twitter api uses to attach a file object to a tweet and 2) the size of
        the file. Currently, the Twitter API allows up to 4 photos or 1 animated
        GIF or video per tweet. This function is written to use the 'simple
        image upload' endpoint provided by Twitter. However, according to
        Twitter, in the future only the 'chunked upload' enpoint which supports
        both images and videos wil be supported for new features.

    lat             : float, optional
        Latitude corresponding to the optional lat parameter in the Twitter API
        which allows users to package the location the tweet is associated with
        along with the messge. (default value is 39.291664)

    long            : float, optional
        Longitude corresponding to the optional long parameter in the Twitter
        API which allows users to package the location the tweet is associated
        with along with the messge. (default value is -76.610726)

    Returns
    -------
    str
         Returns 'Post Successful.' if successful, Error message with exception
         if fails.

    Examples
    --------
    >>> post_tweet(tweepy_api=api, message=msg, media_objects=media_dict)
    """

    media_ids = []

    for val in media_objects.values():
        if len(media_objects) > 0:
            media_ids.append(val['media_id'])
        else:
            pass


    # ensure compliance with current Twitter API media restrictions
    try:
        if len(media_ids) > 4:
            # okay now but must refactor for future if 'chunked media upload' with mix of filetypes
            media_ids = media_ids[:4]
    except Exception as e:
        print(e)


    try:
        tweepy_api.update_status(status=message, lat=latitude,
                                 long=longitude, media_ids=media_ids)
        result = 'Post Successful.'

    except:
        result =  'Error {}: {} Traceback: {}'.format(
            str(sys.exc_info()[0]).split("'")[1],
            sys.exc_info()[1],
            sys.exc_info()[-1])

    return result


def tweet(api_object, files, msg=None):
    """Send tweet, with image if jpeg or png files passed.

    Serves as a wrapper function combining : A) the request for hanlding the
    response object required for including images in a tweet and, B) the post
    method for making a status update to Twitter.

    Parameters
    ----------
    api_object : tweepy.api.API
        A tweepy api object resulting from initializing oauth with Twitter
        api keys

    files      : list
        List of image files. The function forces compliance with the Twitter
        api by ignoring files that are not jpeg or png files.

    msg        : str
        The text to be posted in the body of the tweet. Optionally, users can
        pass a function if the return of the function is a string.  For example,
        if a function my_message() returns a string, my_message() can be passed
        as an argument to the message parameter of the function.

    Returns
    -------
    str
        Returns 'Post Successful.' if successful, Error message with exception
        if it fails.

    Examples
    --------
    >>> tweet(api_object=api_obj, files=files ,msg=function2generate_message)

    >>> tweet(api_object=api_obj, files=['file1.png','file2.jpeg'],msg=None)

    """

    media_ids = (get_media_ids(
        tweepy_api=api_object, img_files=files))

    return (post_tweet(tweepy_api=api_object, message=msg,
            media_objects=media_ids))
