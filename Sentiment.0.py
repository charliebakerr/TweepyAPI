from tweepy import API
from tweepy import OAuthHandler

import User_names
import twitter_credentials
import pandas as pd
import datetime

# Creating client
class TwitterClient():
    
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
        
#Authenticating credentials# 

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_token, twitter_credentials.access_secret)
        return auth
class TweetAnalyzer():
    
#Functionality for analyzing and categorizing content from tweets.
  
  def tweets_to_data_frame(self, df, tweets, user):
    user_from_api = api.get_user(user)
    #sentiment = pd.read_csv('SentimentAnalysis.csv',usecols =['Sentiment']) 
    for tweet in tweets:
        
        df = df.append({'Tweet' : tweet.text,
                   'Handle'     : tweet.user.screen_name, 
                   'TimeStamp'  : tweet.created_at, 
                   'Likes'      : tweet.favorite_count,
                   #Reply count works with premium api
                   #'Replies'    : tweet.reply_count,
                   'Retweets'   : tweet.retweet_count,
                   'TimeSince'  : int((datetime.datetime.now()-tweet.created_at).total_seconds()),
                   #Sentiment needs recalibrating for time periods over a 24hrs for a week reduce time scaling factor or even remove it.
                   'Sentiment'  : (1/(100000*(int((datetime.datetime.now()-tweet.created_at).total_seconds())/3600)*user_from_api.followers_count)) * (( tweet.retweet_count* 5) + (tweet.favorite_count * 0.5))},
                  #'Impact' - time derivative version of this, taken over two instances will deliver impact rating and help detect high impact tweets before the 'alpha' is lost
                  #^ Can introduce a time variable or take two separate instances of csv and manually compute with delta sentiment / delta time.
                  # Alternatively  can introduce time taken to hit certain metric eg, 100 likes/RT's or sentiment score 
                  #'Impact'     : 'sentiment' - sentiment.values/ timeperiod},
                   ignore_index=True)
        
    return df
             
if __name__ == '__main__':
    twitter_client      = TwitterClient()
    tweet_analyzer      = TweetAnalyzer()
    api                 = twitter_client.get_twitter_client_api()  
    users               = User_names.user
    df                  = pd.DataFrame(columns=['Tweet', 'Handle', 'TimeStamp', 'Likes', 'Retweets','TimeSince','Sentiment','Impact'])
                                            
    for user in users:
        #Interacting with twitter api and collecting metrics into df
        tweets              = api.user_timeline(screen_name=user, count=30)
        df                  = tweet_analyzer.tweets_to_data_frame(df=df, tweets=tweets, user=user)
         #Filtering data from last 24hrs
        df1                 = df.query("TimeSince < 86400") 
        #Sorting via sentiment
        df_sorted           = df1.sort_values(by="Sentiment", ascending=False ,kind="mergesort")
        #Extracting top 5
        df_snip             = df_sorted.iloc[:5]
        
    df.to_csv('SentimentAnalysis.csv')
    df_snip.to_csv('SentimentAnalysis.snip.csv')