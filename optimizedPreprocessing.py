from fuzzywuzzy import fuzz
import csv
import re
from datetime import datetime
features = {}
tweets = {}
location = ''

def write_to_file(dictionary, dictname):
	print 'Inside write_to_file'
	with open(dictname + '.py', 'w') as f:
		f.write('content = ' + str(dictionary))
urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
replyRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)'
hashtagRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9]+)'
with open(location + 'content_polluters_tweets.txt','rb') as f:
#with open(location + 'pollutersSample.txt','rb') as f:
	content = csv.reader(f,delimiter = '\t')
	c = 1
	for row in content:
		print "tweets count ", c 
		c += 1
		userId, tweetId, tweet, createdAt = row
		urlsList = []
		if userId not in tweets:
			tweets[userId] = []
		if userId not in features:
			features[userId] = {}
			features[userId]['urlsCount'] = 0
			features[userId]['hashtagsCount'] = 0
			features[userId]['retweetsCount'] = 0
			features[userId]['repliesCount'] = 0
			features[userId]['numOfUrlTweets'] = 0
			features[userId]['tweetsCreatedAt'] = []
			features[userId]['tweetTimeDiff'] = []
			features[userId]['tweetFrequency'] = {}
			features[userId]['tweetSimilarity'] = 0
			retweets = []
		tweets[userId].append(tweet)
		createdAtObj = datetime.strptime(createdAt, '%Y-%m-%d %H:%M:%S')
		urls = re.findall(urlRegex,tweet)
		hashtags = re.findall(hashtagRegex, tweet)
		replies = re.findall(replyRegex, tweet)
		retweets = re.search(r'(RT|retweet|from|via)(?:\b\W*@(\w+))+', tweet)
		urlsCount = len(urls)
		hashtagsCount = len(hashtags)
		repliesCount = len(replies)
		if isinstance(retweets, tuple):
			retweets = retweets.groups()
			retweetsCount = len(retweets)/2
		else:
			retweetsCount = 0
		urlsList.append(urlsCount)
		numOfUrlTweets = sum(1 for url in urlsList if url>0)
		features[userId]['urlsCount'] += urlsCount
		features[userId]['hashtagsCount'] += hashtagsCount
		features[userId]['repliesCount'] += repliesCount
		features[userId]['retweetsCount'] += retweetsCount
		features[userId]['numOfUrlTweets'] += numOfUrlTweets
		features[userId]['tweetsCreatedAt'].append(createdAtObj)
c = 1
for userId in features:
	print "similarity ", c
	temp = features[userId]
	for itemIndex in range(len(temp['tweetsCreatedAt'])):
		
		# if itemIndex != len(temp['tweetsCreatedAt'])-1:
		# 	features[userId]['tweetTimeDiff'].append(\
		# 		abs(temp['tweetsCreatedAt'][itemIndex] -\
		# 		temp['tweetsCreatedAt'][itemIndex+1]).total_seconds())
		timeObj = temp['tweetsCreatedAt'][itemIndex]
		year, month, day = timeObj.date().year, timeObj.date().month, timeObj.date().day
		if (year,month,day) not in features[userId]['tweetFrequency']:
			features[userId]['tweetFrequency'][(year,month,day)] = 1
		else:
			features[userId]['tweetFrequency'][(year,month,day)] += 1
	'''
	tweetSim  = []
	for tweet in tweets[userId]:
		index = tweets[userId].index(tweet)
		for tweetNext in tweets[userId][index:]:
			similarity = fuzz.token_set_ratio(tweet, tweetNext)
			tweetSim.append(similarity)
	numOfTweets = len(tweets[userId])
	if numOfTweets > 1:
			features[userId]['tweetSimilarity'] = sum(tweetSim)/float(((numOfTweets*numOfTweets-1)/2))
	'''
	c += 1
'''
for userId in features:
	for timeObj in features[userId]['tweetsCreatedAt']:
		index = features[userId]['tweetsCreatedAt'].index(timeObj)
		if index != len()-1:
			nextTimeObj = features[userId]['tweetsCreatedAt'][index+1]
			timeDiff = nextTimeObj - timeObj
			timeDiffSec = timeDiff.total_seconds()
			features[userId]['tweetTimeDiff'].append(timeDiffSec)

	for timeObj in features[userId]['tweetsCreatedAt']:
		year, month, day = timeObj.date().year, timeObj.date().month, timeObj.date().day
		if (year,month,day) not in features[userId]['tweetFrequency']:
			features[userId]['tweetFrequency'][(year,month,day)] = 1
		else:
			features[userId]['tweetFrequency'][(year,month,day)] += 1
'''
with open(location + 'content_polluters.txt','rb') as f:
#with open(location + 'pollutersInfoSample.txt','rb') as f:
	content = csv.reader(f,delimiter = '\t')
	c = 1
	for row in content:
		print "userId count ", c
		c += 1
		userId, createdAt, followings, followers, tweetCount, screenNameLength = row[0], row[1], row[3],row[4],row[5], row[6]
		if userId not in features:
			features[userId] = {}
		features[userId]['screenNameLength'] = screenNameLength
		features[userId]['followers'] = followers
		features[userId]['followings'] = followings
		if float(followings) != 0:
			features[userId]['followerFollowingRatio'] = int(followers) / float(followings)
		else:
			features[userId]['followerFollowingRatio'] = 0
		features[userId]['tweetCount'] = tweetCount

with open(location + 'content_polluters_followings.txt', 'rb') as f:
#with open(location + 'pollutersFollowingSample.txt','rb') as f:
	content = csv.reader(f, delimiter = '\t')
	c = 1
	for row in content:
		print "userId followings ", c
		c += 1
		userId, followingSeries = row
		if userId not in features:
			features[userId] = {}
		followingRate = []
		features[userId]['averageFollowingRate'] = 0
		followingSeries = followingSeries.split(',')
		for itemIndex in range(len(followingSeries) - 1):
			followingRate.append(abs(int(followingSeries[itemIndex]) - \
				int(followingSeries[itemIndex + 1])))
			features[userId]['averageFollowingRate'] = sum(followingRate) / len(followingRate)
write_to_file(features, 'features')
write_to_file(tweets, 'tweets')

with open('FeaturesSelected.csv', 'wb') as f:
	writer = csv.writer(f, delimiter = ',', quoting=csv.QUOTE_MINIMAL)
	keys = ['urlsCount', 'numOfUrlTweets', 'hashtagsCount', 'repliesCount', 'retweetsCount', 'tweetSimilarity', \
	'followers', 'followings', 'followerFollowingRatio', 'averageFollowingRate', 'screenNameLength']
	writer.writerow(['userId']+keys)
	for userId in features:
		row = []
		row.append(userId)
		for key in keys:
			if key not in features[userId]:
				features[userId][key] = 0
		row.extend([features[userId][key] for key in keys])
		writer.writerow(row)
