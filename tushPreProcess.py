'''
with open('pollutersSample.txt','rb') as f:
	content = f.readlines()
	for line in content:
		userId, tweetId, tweet = line.split('\t')
		tweets['userId'] = tweet
'''
import csv
import re
from datetime import datetime
user = {}
features = {}
with open('pollutersSample.txt','rb') as f:
	content = csv.reader(f,delimiter = '\t')
	for row in content:
		userId, tweetId, tweet, createdAt = row
		if userId not in user:
			user[userId] = {}
			user[userId]['tweetInfo'] = []
		user[userId]['tweetInfo'].append([tweetId,tweet,createdAt])
with open('pollutersInfoSample.txt','rb') as f:
	content = csv.reader(f,delimiter = '\t')
	for row in content:
		userId, createdAt, followings, followers, tweetCount = row[0], row[1], row[3],row[4],row[5]
		if userId not in user:
			user[userId] = {}
			user[userId]['tweetInfo'] = []
			user[userId]['tweetInfo'].append([00000,'No tweet History', '2009-11-10 15:14:31'])
		if 'profileInfo' not in user[userId]:
			user[userId]['profileInfo'] = []
		user[userId]['profileInfo'].extend([createdAt, followings, followers, tweetCount])
urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
hashTagRegex = '#[A-Za-z0-9]+'
RTRegex = '@[A-Za-zo-9]+'
for userId in user:
	features[userId] = {}
	features[userId]['urlsList'] = []
	features[userId]['hashtagsList'] = []
	features[userId]['retweetsList'] = []
	features[userId]['numOfUrlTweets'] = 0
	features[userId]['tweetsCreatedAt'] = []
	features[userId]['tweetTimeDiff'] = []
	features[userId]['tweetFrequency'] = {}
	numOfTweets = len(user[userId]['tweetInfo'])
	for tweetItem in range(numOfTweets):
		tweet = user[userId]['tweetInfo'][tweetItem][1]
		createdAt = user[userId]['tweetInfo'][tweetItem][2]
		createdAtObj = datetime.strptime(createdAt, '%Y-%m-%d %H:%M:%S')
		#createdAtObj = datetime.strptime('2009-11-10 15:14:31', '%Y-%m-%d %H:%M:%S')
		urls = re.findall(urlRegex,tweet)
		#hashtags = re.findall(hashTagRegex,tweet)
		#retweets = re.findall(RTRegex,tweet)
		hashtags = set(tag for tag in tweet.split() if tag.startswith('#'))
		retweets = set(retweet for retweet in tweet.split() if retweet.startswith('@'))
		#hashtags = []
		#retweets = []
		urlsCount = len(urls)
		hashtagsCount = len(hashtags)
		retweetsCount = len(retweets)
		features[userId]['urlsList'].append(urlsCount)
		features[userId]['hashtagsList'].append(hashtagsCount)
		features[userId]['retweetsList'].append(retweetsCount)
		features[userId]['urlsCount'] = sum(features[userId]['urlsList'])
		features[userId]['hashtagsCount'] = sum(features[userId]['hashtagsList'])
		features[userId]['retweetsCount'] = sum(features[userId]['retweetsList'])
		features[userId]['numOfUrlTweets'] = sum(1 for url in features[userId]['urlsList'] if url>0)
		features[userId]['tweetsCreatedAt'].append(createdAtObj)
	#features[userId]['tweetsCreatedAt'].reverse()
	for tweetTimes in features[userId]['tweetsCreatedAt'][:-1]:
		profileCreateTime = datetime.strptime(user[userId]['profileInfo'][0], '%Y-%m-%d %H:%M:%S')
		index = features[userId]['tweetsCreatedAt'].index(tweetTimes)
		'''
		if index != 0:
		'''
		tweetTimesNext = features[userId]['tweetsCreatedAt'][index+1]
		timeDiff = tweetTimesNext - tweetTimes
		timeDiffSec = timeDiff.total_seconds()
		features[userId]['tweetTimeDiff'].append(timeDiffSec)
		'''
		else:
			timeDiff = tweetTimes -profileCreateTime
			timeDiffSec = timeDiff.total_seconds()
			features[userId]['tweetTimeDiff'].append(timeDiffSec)
		'''
	for tweetTime in features[userId]['tweetsCreatedAt']:
		year, month, day = tweetTime.date().year, tweetTime.date().month, tweetTime.date().day
		if (year,month,day) not in features[userId]['tweetFrequency']:
			features[userId]['tweetFrequency'][(year,month,day)] = 1
		else:
			features[userId]['tweetFrequency'][(year,month,day)] += 1

'''
for user1 in features:
	print user1, 'numOfTweets:', len(user[user1]['tweetInfo']), 'hashtagsCount:', features[user1]['hashtagsCount'], 'urlsCount:' , features[user1]['urlsCount'], 'numOfUrlTweets:', features[user1]['numOfUrlTweets'], 'retweetsCount:', features[user1]['retweetsCount']
'''
for user1 in features:
	print user1
	for key,value in features[user1].iteritems():
		print key, value
	print
