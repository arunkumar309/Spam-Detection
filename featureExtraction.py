from fuzzywuzzy import fuzz
import csv
import re
#from datetime import datetime
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import nltk
import unicodedata
import string
import re
from collections import Counter
from fuzzywuzzy import fuzz
from nltk.stem.snowball import SnowballStemmer
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8')

features = {}
tweets = {}
#location = 'C:\Users\Harini Ravichandran\Documents\ASU Sem 1\Social Media Mining - 598\STEM\social_honeypot_icwsm_2011\\'
#location = "/Users/kannanravindran/Desktop/spammers_detection/Social Honeypot method/social_honeypot_icwsm_2011/"
location = ''
test = False
if test == False:
	content_files = ['content_polluters_tweets.txt', 'legitimate_users_tweets.txt']
	profile_files = ['content_polluters.txt', 'legitimate_users.txt']
	temporal_followings_files = ['content_polluters_followings.txt', 'legitimate_users_followings.txt']
else:
	content_files = ['content_polluters_tweets_sample.txt', 'legitimate_users_tweets_sample.txt']
	profile_files = ['content_polluters_sample.txt', 'legitimate_users_sample.txt']
	temporal_followings_files = ['content_polluters_followings_sample.txt', 'legitimate_users_followings_sample.txt']

featuresList = ['urlsCount', 'numOfUrlTweets', 'hashtagsCount', 'repliesCount', 'retweetsCount', 'tweetSimilarity', 'spamWordsRatio', \
		'followers', 'followings', 'followerFollowingRatio', 'averageFollowingRate', 'screenNameLength']

urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
replyRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)'
hashtagRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9]+)'
stopwords = stopwords.words('english')

def write_dict(dictionary, dictname):
	print 'Inside write_to_file'
	with open(dictname + '.py', 'w') as f:
		f.write('content = ' + str(dictionary))

def write_csv(dictionary, filename):
	with open(filename, 'wb') as f:
		writer = csv.writer(f, delimiter = ',', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['userId']+featuresList)
		for userId in dictionary:
			row = []
			row.append(userId)
			for key in featuresList:
				if key not in dictionary[userId]:
					dictionary[userId][key] = 0
			row.extend([dictionary[userId][key] for key in featuresList])
			writer.writerow(row)

def toString(unicodeData):
	stringOut = unicodedata.normalize('NFKD',unicode(unicodeData)).encode('ascii','ignore')
	return stringOut

def initialize_features(category, userId):
	global features
	features[category][userId] = {}
	features[category][userId]['urlsCount'] = 0
	features[category][userId]['hashtagsCount'] = 0
	features[category][userId]['retweetsCount'] = 0
	features[category][userId]['repliesCount'] = 0
	features[category][userId]['numOfUrlTweets'] = 0
	features[category][userId]['tweetsCreatedAt'] = []
	features[category][userId]['tweetTimeDiff'] = []
	features[category][userId]['tweetFrequency'] = {}
	features[category][userId]['tweetSimilarity'] = 0

def get_tweets_per_day(category):
	c = 1
	global features
	for userId in features[category]:
		print "tweetFrequency ", c
		temp = features[category][userId]
		for itemIndex in range(len(temp['tweetsCreatedAt'])):
			timeObj = temp['tweetsCreatedAt'][itemIndex]
			year, month, day = timeObj.date().year, timeObj.date().month, timeObj.date().day
			if (year,month,day) not in features[category][userId]['tweetFrequency']:
				features[category][userId]['tweetFrequency'][(year,month,day)] = 1
			else:
				features[category][userId]['tweetFrequency'][(year,month,day)] += 1
		c += 1

def extract_tweet_features(row, category):
	global tweets, features
	urlsList = []
	userId, tweetId, tweet, createdAt = row
	if userId not in tweets[category]:
		tweets[category][userId] = []
	if userId not in features[category]:
		initialize_features(category, userId)
	tweets[category][userId].append(tweet)
	createdAtObj = datetime.datetime.strptime(createdAt, '%Y-%m-%d %H:%M:%S')
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
	features[category][userId]['urlsCount'] += urlsCount
	features[category][userId]['hashtagsCount'] += hashtagsCount
	features[category][userId]['repliesCount'] += repliesCount
	features[category][userId]['retweetsCount'] += retweetsCount
	features[category][userId]['numOfUrlTweets'] += numOfUrlTweets
	features[category][userId]['tweetsCreatedAt'].append(createdAtObj)

def extract_content_features(location, filename, category):
	global features, tweets
	with open(location + filename, 'rb') as f:
	#with open(location + 'pollutersSample.txt','rb') as f:
		content = csv.reader(f, delimiter = '\t')
		c = 1
		features[category] = {}
		tweets[category] = {}
		for row in content:
			print "tweets count ", c 
			c += 1
			extract_tweet_features(row, category)
		get_tweets_per_day(category)

def extract_profile_features(location, filename, category):
	global features
	with open(location + filename, 'rb') as f:
	#with open(location + 'pollutersInfoSample.txt','rb') as f:
		content = csv.reader(f, delimiter = '\t')
		c = 1
		for row in content:
			print "userId count ", c
			c += 1
			userId, createdAt, followings, followers, tweetCount, screenNameLength = row[0], row[1], row[3],row[4],row[5], row[6]
			if userId not in features[category]:
				initialize_features(category,userId)
				#features[category][userId] = {}
			features[category][userId]['screenNameLength'] = int(screenNameLength)
			features[category][userId]['followers'] = int(followers)
			features[category][userId]['followings'] = int(followings)
			if float(followings) != 0:
				features[category][userId]['followerFollowingRatio'] = int(followers) / float(followings)
			else:
				features[category][userId]['followerFollowingRatio'] = 0
			features[category][userId]['tweetCount'] = int(tweetCount)

def extract_following_rate(location, filename, category):
	global features
	with open(location + filename, 'rb') as f:
	#with open(location + 'pollutersFollowingSample.txt','rb') as f:
		content = csv.reader(f, delimiter = '\t')
		c = 1
		for row in content:
			print "userId followings ", c
			c += 1
			userId, followingSeries = row
			if userId not in features[category]:
				initialize_features(category, userId)
				#features[category][userId] = {}
			followingRate = []
			features[category][userId]['averageFollowingRate'] = 0
			followingSeries = followingSeries.split(',')
			for itemIndex in range(len(followingSeries) - 1):
				followingRate.append(abs(int(followingSeries[itemIndex]) - \
					int(followingSeries[itemIndex + 1])))
				features[category][userId]['averageFollowingRate'] = sum(followingRate) / len(followingRate)

def get_unique_words(tweetsList):
	punctuations = string.punctuation
	tweetsUniqueString = ''
	for tweet in tweetsList:
		urls = re.findall(urlRegex,tweet)
		hashtags = re.findall(hashtagRegex, tweet)
		replies = re.findall(replyRegex, tweet)
		retweets = re.search(r'(RT|retweet|from|via)(?:\b\W*@(\w+))+', tweet)
		if isinstance(retweets, tuple):
			retweets = retweets.groups()
		else:
			retweets = []
		tweetWords = []
		tweetSplit = tweet.split()
		tweetWords = list(set(tweetSplit))
		temp = ' '.join(word.lower() for word in tweetWords if word not in urls and word not in hashtags and word not in replies and word not in retweets)
		temp = ''.join(ch for ch in temp if ch not in punctuations)
		tweetsUniqueString += temp
		tweetsUniqueString += ' '
	return tweetsUniqueString

def get_spam_words(tweetsUniqueString):
	global stopwords
	tweetTokens = tweetsUniqueString.lower().split()
	tweetTokens = [word for word in tweetTokens if word not in stopwords]
	tweetsString = ' '.join(word for word in tweetTokens)
	tweetTokens = TweetTokenizer().tokenize(tweetsString)
	tweetTokens = [toString(word) for word in tweetTokens]
	wordFreq = nltk.FreqDist(tweetTokens)
	numOfWords = len(wordFreq)
	numOfSpam = int(numOfWords*0.10)
	spamWords = wordFreq.most_common(numOfSpam)
	spamWordsDict = dict(spamWords)
	return spamWordsDict


def get_spam_words_frequency(spamWordsDict, category):
	global tweets, features, stopwords
	tweetsDict = tweets[category]
	for userId in tweetsDict:
		matchedSpamCount= 0
		tweetsList = tweetsDict[userId]
		tweetsList = get_unique_words(tweetsList)
		tweetWords = tweetsList.split()
		tweetWords = [word for word in tweetWords if word not in stopwords]
		tweetWords = dict(Counter(tweetWords))
		totalWords = len(tweetWords)
		for word in tweetWords:
			if word in spamWordsDict:
				matchedSpamCount += tweetWords[word]
		if float(totalWords) != 0:
			features[category][userId]['spamWordsRatio'] = matchedSpamCount / float(totalWords)
		else:
			features[category][userId]['spamWordsRatio'] = 0


def extract_spam():
	global tweets, stopwords
	urlRegex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
	replyRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)'
	hashtagRegex = '(?<=^|(?<=[^a-zA-Z0-9-_\.]))#([A-Za-z]+[A-Za-z0-9]+)'
	stopwords = [toString(word).lower() for word in stopwords]
	tweetTokens = []
	tweetsUniqueString = ''
	c = 1
	for userId in tweets['spammers']:
		print "spam words ", c
		c += 1
		tweetsList = tweets['spammers'][userId]
		tweetsUniqueString += get_unique_words(tweetsList)
		tweetsUniqueString += ' '
	spamWordsDict = get_spam_words(tweetsUniqueString)

	for category in ('spammers', 'legitimate'):
		get_spam_words_frequency(spamWordsDict, category)

def getMostTweetedDate(mostTweeted,category):
	global features
	mostTweeted[category] = {}
	for userId in features[category]:
		mostTweeted[category][userId] = {}
		#print features[category][userId]['tweetFrequency']
		mostCommon = nltk.FreqDist(features[category][userId]['tweetFrequency'])\
		.most_common(1)
		if len(mostCommon) > 0:
			mcYear, mcMonth, mcDay = mostCommon[0][0][0], mostCommon[0][0][1],mostCommon[0][0]\
			[2]
			mostTweeted[category][userId]['YMD'] = (mcYear,mcMonth,mcDay)
			mostTweeted[category][userId]['count'] = mostCommon[0][1]
		else:
			mostTweeted[category][userId]['YMD'] = ()
			mostTweeted[category][userId]['count'] = 0
	return mostTweeted

def getToStemTweets(tweetsToStem,mostTweeted,category):
	global tweets, features
	tweetsToStem[category] = {}
	for userId in features[category]:
		tweetsToStem[category][userId] = []
		tweetIndices = []
		timeObjs = features[category][userId]['tweetsCreatedAt']
		for timeObj in timeObjs:
			date = (timeObj.year, timeObj.month, timeObj.day)
			if date == mostTweeted[category][userId]['YMD']:
				tweetIndices.append(timeObjs.index(timeObj))
		for index in tweetIndices:
			tweetsToStem[category][userId].append(tweets[category][userId][index])
	return tweetsToStem

def stemming(tweetsToCheck,tweetsToStem,category):
	stemmer = SnowballStemmer('english')
	punctuations = string.punctuation
	tweetsToCheck[category] = {}
	for userId in tweetsToStem[category]:
		tweetsList = tweetsToStem[category][userId]
		tweetsToCheck[category][userId] = []
		for tweet in tweetsList:
			tweet = ''.join(ch for ch in tweet if ch not in punctuations)
			tweet = tweet.lower().split()
			tweet = [word for word in tweet if word not in stopwords]
			tweet = ' '.join(word for word in tweet)
			tweet = stemmer.stem(tweet)
			tweet = toString(tweet)
			tweetsToCheck[category][userId].append(tweet)
	return tweetsToCheck

def extract_similarities():
	global features
	mostTweeted = {}
	tweetsToStem = {}
	tweetsToCheck = {}
	for category in ('spammers', 'legitimate'):
		mostTweeted = getMostTweetedDate(mostTweeted,category)
		tweetsToStem = getToStemTweets(tweetsToStem,mostTweeted,category)
		tweetsToCheck = stemming(tweetsToCheck,tweetsToStem,category)
		c = 1
		for userId in tweetsToCheck[category]:
			print "similarity ", c
			c += 1
			tweetSim  = []
			#print c, len(tweetsToCheck[category][userId])
			for tweet in tweetsToCheck[category][userId]:
				index = tweetsToCheck[category][userId].index(tweet)
				#print 'Comparing tweet ', index, 'with other tweets'
				for tweetNext in tweetsToCheck[category][userId][index+1:]:
					similarity = fuzz.token_set_ratio(tweet, tweetNext)
					tweetSim.append(similarity)
			numOfTweets = len(tweetsToCheck[category][userId])
			if numOfTweets > 1:
					features[category][userId]['tweetSimilarity']= sum(tweetSim)/(100*float(numOfTweets*(numOfTweets-1)/2))

def get_category(filename):
	if 'polluters' in filename:
		category = 'spammers'
	else:
		category = 'legitimate'
	return category

if __name__ == '__main__':
	for filename in content_files:
		category = get_category(filename)
		extract_content_features(location, filename, category)
	for filename in profile_files:
		category = get_category(filename)
		extract_profile_features(location, filename, category)
	for filename in temporal_followings_files:
		category = get_category(filename)
		extract_following_rate(location, filename, category)
	extract_spam()
	extract_similarities()
	for category in ('spammers', 'legitimate'):
		write_dict(features[category], 'features_' + category)
		write_csv(features[category], 'FeaturesSelected_' + category+'.csv')
