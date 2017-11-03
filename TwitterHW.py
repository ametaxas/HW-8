# Import statements
import unittest
import sqlite3
import requests
import json
import re
import tweepy
import twitter_info # still need this in the same directory, filled out

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

# And we've provided the setup for your cache. But we haven't written any functions for you, so you have to be sure that any function that gets data from the internet relies on caching.
CACHE_FNAME = "twitter_cache.json"
try: #looks to see if there is alrady a cache file in the current repository, and if it exists, open it and load it into the cache_diction
    cache_file = open(CACHE_FNAME,'r') 
    cache_contents = cache_file.read()
    cache_file.close()
    cache_diction = json.loads(cache_contents)
except: #if not, initalize a cache_diction that will later be loaded into a cache
    cache_diction = {}

## [PART 1]

# Here, define a function called get_tweets that searches for all tweets referring to or by "umsi"
# Your function must cache data it retrieves and rely on a cache file!
def get_tweets():
    if umsi not in cache_diction: #if the search term isn't in the cache...
        print ('retreiving from the internet')
        umsi_timeline = api.user_timeline('umsi', count = 200) #retreives the 200 most recent tweets on the umsi timeline
        cache_diction['umsi'] = umsi_timeline
        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(cache_diction)) #...add it to the cache!
        cache_file.close()
    else:
        print ('using cache')
    return cache_diction['umsi'] 

## [PART 2]
# Create a database: tweets.sqlite,
# And then load all of those tweets you got from Twitter into a database table called Tweets, with the following columns in each row:
## tweet_id - containing the unique id that belongs to each tweet
## author - containing the screen name of the user who posted the tweet (note that even for RT'd tweets, it will be the person whose timeline it is)
## time_posted - containing the date/time value that represents when the tweet was posted (note that this should be a TIMESTAMP column data type!)
## tweet_text - containing the text that goes with that tweet
## retweets - containing the number that represents how many times the tweet has been retweeted

# Below we have provided interim outline suggestions for what to do, sequentially, in comments.

# 1 - Make a connection to a new database tweets.sqlite, and create a variable to hold the database cursor.
conn = sqlite3.connect('tweets.sqlite')
cur = conn.cursor()
# # 2 - Write code to drop the Tweets table if it exists, and create the table (so you can run the program over and over), with the correct (4) column names and appropriate types for each.
# # HINT: Remember that the time_posted column should be the TIMESTAMP data type!
cur.execute('DROP TABLE IF EXISTS Tweets') #removes the table if it exists so we can create the table over and over again without causing an error
cur.execute('CREATE TABLE Tweets (tweet_id TEXT, author TEXT, time_posted TEXT, tweet_text TEXT, retweets INTEGER)') #creates the table and specifies the type of each column
# 3 - Invoke the function you defined above to get a list that represents a bunch of tweets from the UMSI timeline. Save those tweets in a variable called umsi_tweets.
tweets = get_tweets() #retrieves 200 tweets from the umsi timeline and stores it in a variable tweets

# 4 - Use a for loop, the cursor you defined above to execute INSERT statements, that insert the data from each of the tweets in umsi_tweets into the correct columns in each row of the Tweets database table.
for tweet in tweets:
    info = (tweet['id'], tweet['user']['screen_name'], tweet['created_at'], tweet['text'], tweet['retweet_count']) #tuple representing tweet information to be distributed into the tabel
    cur.execute('INSERT INTO Tweets (tweet_id, author, time_posted, tweet_text, retweets) VALUES (?,?,?,?,?)', info) #insert tuple into the table

#  5- Use the database connection to commit the changes to the database
conn.commit() #force the data to be written to the database file
# You can check out whether it worked in the SQLite browser! (And with the tests.)
## [PART 3] - SQL statements
# Select all of the tweets (the full rows/tuples of information) from umsi_tweets and display the date and message of each tweet in the form:
    # Mon Oct 09 16:02:03 +0000 2017 - #MondayMotivation https://t.co/vLbZpH390b
    #
    # Mon Oct 09 15:45:45 +0000 2017 - RT @MikeRothCom: Beautiful morning at @UMich - It’s easy to forget to
    # take in the view while running from place to place @umichDLHS  @umich…
# Include the blank line between each tweet.
cur.execute('SELECT time_posted, tweet_text FROM Tweets')
for row in cur: #iterate through the cursor to print the time and text
    print (row[0] + ' - ' + row[1])
# Select the author of all of the tweets (the full rows/tuples of information) that have been retweeted MORE
# than 2 times, and fetch them into the variable more_than_2_rts.
# Print the results
cur.execute('SELECT author FROM Tweets WHERE retweets > 2')
more_than_2_rts = [author[0] for author in cur] #accumulate authors with tweets that have more than 2 retweets into the variable more_than_2_rts
print (more_than_2_rts) #in this case authors are only umsi as I used the user_timeline method in my search

if __name__ == "__main__":
    unittest.main(verbosity=2)
