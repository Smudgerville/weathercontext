from twitter import *
import os, requests, json
from tweet import makeGraph, sendTweet

cities_covered = ["Berlin"]

def getCityFromTweet(s):
    url = "https://api.dandelion.eu/datatxt/nex/v1/?text=%s&include=types&token=%s" % (s, os.environ["DANDELION"])
    r = requests.get(url)
    json_data = json.loads(r.text)

    print (s)
    print (json_data)

    # Parses the response from Dandelion and looks for matches of the
    # type http://dbpedia.org/ontology/Place, then returns the first
    # match's name.
    for annotation in json_data["annotations"]:
        if "http://dbpedia.org/ontology/Place" in annotation["types"]:
            return annotation["label"]

auth = OAuth(os.environ["ACCESS_TOKEN"], os.environ["ACCESS_SECRET"], os.environ["TWITTER_KEY"], os.environ["TWITTER_SECRET"])

# Authentifies with Twitter
t = Twitter(auth=auth)

# And with twitter stream
twitter_stream = TwitterStream(auth=auth, domain='stream.twitter.com')

# And with twitter upload 
t_upload = Twitter(domain='upload.twitter.com', auth=auth)

# Gets only the mentions to the account
iterator = twitter_stream.statuses.filter(track="@weathercontext")

for msg in iterator:

	# Gets some data from the tweet
    username = msg["user"]["screen_name"]
    status_id = msg["id_str"]
    tweet_contents = msg["text"]

    # Parses the city
    city = getCityFromTweet(tweet_contents.replace("@weathercontext", ""))
    print (city)
    if city == None:
        status_text = "@%s Sorry, my programmer wasn't smart enough for me to understand you." % username
    	t.statuses.update(status=status_text, in_reply_to_status_id=status_id)
    elif city not in cities_covered:
        status_text = "@%s I don't have weather data for %s yet. But you seem like a nice person, I'll go fetch it and come back to you." % (username, city)
    	t.statuses.update(status=status_text, in_reply_to_status_id=status_id)
    else:
    	title, plt = makeGraph(city)
    	status_text = "@%s %s" % (username, title)
    	sendTweet(status_text, plt, status_id)

    print("Tweeting to %s..." % username)
    