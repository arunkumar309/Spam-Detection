from fuzzywuzzy import fuzz
import csv
import re
from datetime import datetime
user = {}
features = {}
tweets = {}
location = "C:\Users\Harini Ravichandran\Documents\ASU Sem 1\Social Media Mining - 598\STEM\social_honeypot_icwsm_2011\\"

def write_to_file(dictionary):
	print 'Inside write_to_file'
	with open('featuresDict.py', 'w') as f:
		f.write('content = ' + str(dictionary))

with open(location + 'content_polluters_tweets.txt','rb') as f:
	content = csv.reader(f,delimiter = '\t')
	c = 1
	for row in content:
		print "tweets count ", c 
		c += 1
		userId, tweetId, tweet, createdAt = row
		if userId not in user:
			user[userId] = {}
			user[userId]['tweetInfo'] = []
		user[userId]['tweetInfo'].append([tweetId,tweet,createdAt])
with open(location + 'content_polluters.txt','rb') as f:
	content = csv.reader(f,delimiter = '\t')
	c = 1
	for row in content:
		print "userId count ", c
		c += 1
		userId, createdAt, followings, followers, tweetCount, screenNameLength = row[0], row[1], row[3],row[4],row[5], row[6]
		if userId not in user:
			user[userId] = {}
			user[userId]['tweetInfo'] = []
			user[userId]['tweetInfo'].append([00000,'No tweet History', '2009-11-10 15:14:31'])
		if 'profileInfo' not in user[userId]:
			user[userId]['profileInfo'] = []
		user[userId]['profileInfo'].extend([createdAt, followings, followers, tweetCount, screenNameLength])
with open(location + 'content_polluters_followings.txt', 'rb') as f:
	content = csv.reader(f, delimiter = '\t')
	c = 1
	for row in content:
		print "userId followings ", c
		c += 1
		userId, followingSeries = row
		if userId not in user:
			user[userId] = {}
			user[userId]['profileInfo'] = ['', '', '', '', '']
		user[userId]['profileInfo'].append(followingSeries)
urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
hashTagRegex = '#[A-Za-z0-9]+'
replyRegex = '@[A-Za-zo-9]+'
c = 1
for userId in user:
	print c
	c += 1
	tweets[userId] = []
	features[userId] = {}
	urlsList = []
	hashtagsList = []
	repliesList = []
	retweetsList = []
	tweetSim = []
	followingRate = []
	tweetsCreatedAt = []
	numOfTweets = len(user[userId]['tweetInfo'])
	features[userId]['numOfUrlTweets'] = 0
	features[userId]['tweetTimeDiff'] = []
	features[userId]['tweetFrequency'] = {}
	features[userId]['tweetSimilarity'] = 0
	features[userId]['averageFollowingRate'] = 0
	features[userId]['followerFollowingRatio'] = int(user[userId]['profileInfo'][2]) / float(user[userId]['profileInfo'][1])
	features[userId]['followers'] = user[userId]['profileInfo'][2]
	features[userId]['tweetCount'] = user[userId]['profileInfo'][3]
	features[userId]['followings'] = user[userId]['profileInfo'][1]
	features[userId]['screenNameLength'] = user[userId]['profileInfo'][4]
	for tweetItem in range(numOfTweets):
		tweet = user[userId]['tweetInfo'][tweetItem][1]
		tweets[userId].append(tweet)
		createdAt = user[userId]['tweetInfo'][tweetItem][2]
		createdAtObj = datetime.strptime(createdAt, '%Y-%m-%d %H:%M:%S')
		urls = re.findall(urlRegex,tweet)
		hashtags = set(tag for tag in tweet.split() if tag.startswith('#'))
		replies = set(reply for reply in tweet.split() if reply.startswith('@'))
		retweets = set(retweet for retweet in tweet.split() if retweet.startswith('RT'))
		urlsCount = len(urls)
		hashtagsCount = len(hashtags)
		repliesCount = len(replies)
		retweetsCount = len(retweets)
		urlsList.append(urlsCount)
		hashtagsList.append(hashtagsCount)
		repliesList.append(repliesCount)
		retweetsList.append(retweetsCount)
		tweetsCreatedAt.append(createdAtObj)
	features[userId]['urlsCount'] = sum(urlsList)
	features[userId]['hashtagsCount'] = sum(hashtagsList)
	features[userId]['repliesCount'] = sum(repliesList)
	features[userId]['retweetsCount'] = sum(retweetsList)
	features[userId]['numOfUrlTweets'] = sum(1 for url in urlsList if url>0)
	#features[userId]['tweetsCreatedAt'].reverse()
	for tweetTimes in tweetsCreatedAt[:-1]:
		profileCreateTime = datetime.strptime(user[userId]['profileInfo'][0], '%Y-%m-%d %H:%M:%S')
		index = tweetsCreatedAt.index(tweetTimes)
		tweetTimesNext = tweetsCreatedAt[index+1]
		timeDiff = tweetTimesNext - tweetTimes
		timeDiffSec = timeDiff.total_seconds()
		features[userId]['tweetTimeDiff'].append(timeDiffSec)
	for tweetTime in tweetsCreatedAt:
		year, month, day = tweetTime.date().year, tweetTime.date().month, tweetTime.date().day
		if (year,month,day) not in features[userId]['tweetFrequency']:
			features[userId]['tweetFrequency'][(year,month,day)] = 1
		else:
			features[userId]['tweetFrequency'][(year,month,day)] += 1
	for tweet in tweets[userId]:
		index = tweets[userId].index(tweet)
		for tweetNext in tweets[userId][index:]:
			similarity = fuzz.token_set_ratio(tweet, tweetNext)
			tweetSim.append(similarity)
	if numOfTweets>1:
		features[userId]['tweetSimilarity'] = sum(tweetSim)/float(((numOfTweets*numOfTweets-1)/2))
	followingSeries = user[userId]['profileInfo'][5].split(',')
	for itemIndex in range(len(followingSeries) - 1):
		followingRate.append(abs(int(followingSeries[itemIndex]) - \
			int(followingSeries[itemIndex + 1])))
	features[userId]['averageFollowingRate'] = sum(followingRate) / len(followingRate)

write_to_file(features)

with open('FeaturesSelected.csv', 'wb') as f:
	writer = csv.writer(f, delimiter = ',', quoting=csv.QUOTE_MINIMAL)
	keys = ['urlsCount', 'numOfUrlTweets', 'hashtagsCount', 'repliesCount', 'retweetsCount', 'tweetSimilarity', \
	'followers', 'followings', 'followerFollowingRatio', 'averageFollowingRate', 'screenNameLength']
	writer.writerow(keys)
	for userId in features:
		row = [features[userId][key] for key in keys]
		writer.writerow(row)