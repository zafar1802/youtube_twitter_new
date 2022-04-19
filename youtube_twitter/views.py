from traceback import print_tb
from django.urls import reverse_lazy
import requests
import logging, logging.config
import sys
from dateutil import parser
from datetime import datetime, tzinfo
from twython import Twython
import json

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

logging.config.dictConfig(LOGGING)

from isodate import parse_duration
import tweepy
from django.conf import settings
from django.shortcuts import redirect, render

from django.contrib.auth import logout as django_logout

from django.contrib.auth.decorators import login_required
@login_required(login_url='/login')
def index(request):
    
    videos = []

    channels=[]
    
    date=[]
    
     # Chanells code StartL
    subscription_url = 'https://www.googleapis.com/youtube/v3/subscriptions'
    
    params = {
            "part": "snippet, contentDetails",
           "channelId":settings.YOUTUBE_CHANNEL_ID,
             'maxResults' : 49,
             "order":"alphabetical",
            'key' : settings.YOUTUBE_DATA_API_KEY
        }
    
    r = requests.get(subscription_url, params=params)
    # logging.info("result is:",params)
    logging.info(r.content)
    # print(r)
    results = r.json()['items']
    for result in results:
        channel_data = {
                "name":result["snippet"]['title'],
                "id":result["snippet"]["resourceId"]["channelId"],
                'newContent':result["contentDetails"]["newItemCount"] if("newItemCount" in result["contentDetails"])else 0
            }

            
        channels.append(channel_data)

    if request.method == 'POST':
        
       

        #channels endL
        
        video_url = 'https://www.googleapis.com/youtube/v3/videos'
        search_url = 'https://www.googleapis.com/youtube/v3/search'

        video_ids = []
        if("search" in request.POST):
            logging.info('in if')
            
         
            search_params = {
            'part' : 'snippet', 
            'q' : request.POST['search'],
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'maxResults' : 9,
            'type' : 'video',
            }
            r = requests.get(search_url, params=search_params)
            # logging.debug(r)
            results = r.json()['items']
           
            for result in results:
                video_ids.append(result['id']['videoId'])
        else:
            logging.info('in else')
            logging.info(request.POST['goto'])
            search_params = {
            "part":"snippet",
            "channelId":request.POST['goto'],
            "order":"date",
            'maxResults' : 9,
            'type' : 'video',
            "key" : settings.YOUTUBE_DATA_API_KEY,
            }
            r = requests.get(search_url, params=search_params)
            logging.info(r.content)
            logging.info("logging.debug(r)")
            results = r.json()['items']

            for result in results:
                video_ids.append(result['id']['videoId'])
            
      
        video_params = {
            'key' : settings.YOUTUBE_DATA_API_KEY,
            'part' : 'snippet,contentDetails, statistics',
            'id' : ','.join(video_ids),

        }
        r = requests.get(video_url, params=video_params)
        results = r.json()['items']
        for result in results:
            
            video_data = {
                'title' : result['snippet']['title'],
                'id' : result['id'],
                'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'thumbnail' : result['snippet']['thumbnails']['high']['url'],
                'x' : result['snippet']['channelTitle'],
                'like' : result['statistics']['likeCount'] if ("likeCount" in result['statistics']) else "0",
                'views' : result['statistics']['viewCount'],
                'comments':result['statistics']['commentCount'] if ("commentCount" in result['statistics']) else "0",
                # 'date' : int(str(datetime.now()-(parser.parse(result['snippet']['publishedAt']).replace(tzinfo=None)))[:2]),
                'date' : (datetime.now() - datetime.strptime(result['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")).total_seconds() / 60 
                # 'current_date' : datetime.now(),
                
                # 'difference' : video_data['current_date'] - video_data['date'].replace(tzinfo=None)
            }            
            videos.append(video_data)
        print(videos[0])
# twitter 



    # tweets = api.user_timeline(id='python', count=200)
    # tweets_extended = api.user_timeline(id='python', tweet_mode='extended', count=200)
 
# Show one tweet's JSON
    # tweet = tweets[0]
    # print(tweet._json)
        

    
    context = {
        'videos' : videos,
        'channels' : channels,
        # 'trend' : trends_result[0]['trends'][:10],
        # 'time_delta':timedelta
    }

    return render(request, 'index.html', context)

def twitter(request):
    # Search tweets

    auth = tweepy.OAuthHandler('lmi9wxZFfoKbsQsFHnS0b2wm1', 'mBdxtC2bi5QQsChY5mxGCP0eUbheoE2K7NNSlAn9TjjiHHqurO')
    auth.set_access_token('1308320106955575296-xTOiFToEm9vbI3Ylhp7Gdi3Gpkrvmp', 'ZKYs9xo1zQEuGakbO69PzTGcF7AWJSCMFtZF2wXBi45DH')
    api = tweepy.API(auth)
    trends_result = api.get_place_trends(1)
    dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
    if request.method == 'POST':
        python_tweets = Twython('lmi9wxZFfoKbsQsFHnS0b2wm1','mBdxtC2bi5QQsChY5mxGCP0eUbheoE2K7NNSlAn9TjjiHHqurO' )
        query = {'q': request.POST['search'],
        'result_type': 'popular',
        'count': 10,
        'lang': 'en',
        }
        dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}
        for status in python_tweets.search(**query)['statuses']:
            dict_['user'].append(status['user']['screen_name'])
            dict_['date'].append(status['created_at'])
            dict_['text'].append(status['text'])
            dict_['favorite_count'].append(status['favorite_count'])

    
    context = {
        'trend' : trends_result[0]['trends'][:10],
        'user': dict_['user'],
        'text': dict_['text']
    }
    
    return render(request, 'twitter.html', context)


def login(request):
    return render(request, 'login.html')


@login_required
def logout(request):
    django_logout(request)
    return redirect(reverse_lazy('youtube_twitter:home'))